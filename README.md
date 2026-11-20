# Proxy do WMS do IPE-DF para o JOSM

Proxy local que permite usar no [JOSM](https://josm.openstreetmap.de/) os serviços
WMS da [IPE-DF](https://catalogo.ipe.df.gov.br/) (Infraestrutura de Dados Espaciais do
Distrito Federal), como a camada de Regiões Administrativas (`geonode:regioes_administrativas`).

## O problema

O GeoServer da IPE-DF responde **HTTP 200 com corpo vazio** a qualquer pedido cujo
`User-Agent` contenha a palavra `Java`. O JOSM sempre se identifica como
`JOSM/1.5 (...) Java/21...`, então ao adicionar o WMS ele recebe um arquivo vazio e mostra:

```
Não é possível analisar lista de camada WMS.
javax.xml.stream.XMLStreamException: ParseError at [row,col]:[1,1]
Message: Fim prematuro do arquivo.
```

| User-Agent | GetCapabilities |
| --- | --- |
| `Mozilla/5.0`, `QGIS/34000`, `JOSM/1.5`, vazio | 1,4 MB (normal) |
| `Java`, `java`, `JOSM/1.5 (...) Java/21.0.5` | vazio |

O mesmo vale para o `GetMap`: as imagens também chegam vazias.

## Como o proxy resolve

1. Escuta só na própria máquina, em `http://127.0.0.1:18765`.
2. Repassa ao IPE-DF os pedidos que começam com `/geoserver/`, trocando o `User-Agent`.
3. No `GetCapabilities`, reescreve os endereços `http(s)://catalogo.ipe.df.gov.br/geoserver`
   para o próprio proxy. Sem isso, o JOSM leria a lista de camadas pelo proxy e depois
   pediria os mapas direto ao IPE-DF, sendo bloqueado de novo.

Usa só a biblioteca padrão do Python 3.

## Uso

```powershell
python proxy_ipe_josm.py
```

Deixe o terminal aberto enquanto usar o JOSM. Para outra porta: `python proxy_ipe_josm.py 19000`.

No JOSM: **Imagens → Preferências de imagens → + WMS**, com a URL:

```
http://127.0.0.1:18765/geoserver/ows?service=WMS&request=GetCapabilities
```

Escolha a camada desejada (por exemplo `geonode:regioes_administrativas`). Para parar o
proxy, `Ctrl+C` no terminal.

## Licença dos dados

A camada `geonode:regioes_administrativas` ("Regiões Administrativas do Distrito Federal
em 2026") está marcada como **domínio público** nos metadados do catálogo. Confira a
licença de cada camada antes de usá-la no OpenStreetMap.
