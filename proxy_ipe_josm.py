"""Proxy local para usar o WMS do IPE-DF no JOSM.

O GeoServer do IPE-DF devolve resposta vazia para User-Agent que contenha "Java",
e o JOSM sempre se identifica com "... Java/xx". Este proxy repassa os pedidos
com outro User-Agent e reescreve, no GetCapabilities, os endereços do IPE para
o próprio proxy (senão o JOSM pediria os mapas direto ao IPE e seria bloqueado).

Uso:  python proxy_ipe_josm.py [porta]      (porta padrão: 18765)
No JOSM (Imagens > Preferências de imagens > + WMS), URL:
  http://127.0.0.1:18765/geoserver/ows?service=WMS&request=GetCapabilities
"""
import http.server
import sys
import urllib.error
import urllib.request

ORIGEM = "https://catalogo.ipe.df.gov.br"
PORTA = int(sys.argv[1]) if len(sys.argv) > 1 else 18765
LOCAL = f"http://127.0.0.1:{PORTA}"
USER_AGENT = "JOSM-proxy-ipe/1.0"
REESCREVER = (b"https://catalogo.ipe.df.gov.br/geoserver", b"http://catalogo.ipe.df.gov.br/geoserver")


class Repasse(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/geoserver/"):
            self.send_error(404, "Somente /geoserver/ é repassado")
            return
        pedido = urllib.request.Request(ORIGEM + self.path, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(pedido, timeout=60) as resp:
                corpo = resp.read()
                tipo = resp.headers.get("Content-Type", "application/octet-stream")
                status = resp.status
        except urllib.error.HTTPError as erro:
            corpo, tipo, status = erro.read(), erro.headers.get("Content-Type", "text/plain"), erro.code
        except OSError as erro:
            self.send_error(502, f"Falha ao acessar o IPE: {erro}")
            return
        if "xml" in tipo:
            for antigo in REESCREVER:
                corpo = corpo.replace(antigo, LOCAL.encode() + b"/geoserver")
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, formato, *args):
        print(self.address_string(), formato % args)


if __name__ == "__main__":
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", PORTA), Repasse)
    print(f"Proxy do IPE-DF em {LOCAL}  (Ctrl+C para parar)")
    print(f"URL para o JOSM: {LOCAL}/geoserver/ows?service=WMS&request=GetCapabilities")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
