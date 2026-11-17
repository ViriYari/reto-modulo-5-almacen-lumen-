# Almacén Lumen

Tienda de práctica del reto **QA Cloud-Native: automatización con IA generativa**.
Vende cerámica, textil, iluminación y escritorio. El catálogo no se teclea a mano:
sale de Faker con la semilla `20261117`, así que cualquier máquina obtiene los
mismos 24 productos.

La interfaz corre en [http://127.0.0.1:4789](http://127.0.0.1:4789). Hay cuatro
filtros, un carrito y un checkout que devuelve un folio `LM-####`.

## Cómo correrlo

Hace falta Node 20 o superior. Python 3.11 solo para las pruebas de pantalla.

```bash
npm install
npm run datos
npm start
```

En otra terminal, con la tienda ya encendida:

```bash
npm test
npm run smoke
npm run load:green
npm run load:red
```

`load:red` baja el SLA de 800 ms a 1 ms. Tiene que terminar con código 1: ese
es el quality gate deteniendo el deploy. `load:green` tiene que terminar en 0.

Pruebas de pantalla:

```bash
python3 -m venv e2e/.venv
source e2e/.venv/bin/activate
pip install -r e2e/requirements.txt
python -m playwright install chromium
pytest e2e
```

En Windows el entorno queda en `e2e\.venv\Scripts\activate`.

Contrato y contenedor:

```bash
npm run pact:consumer
npm start
npm run pact:provider
docker build -t almacen-lumen .
docker run --rm -p 4789:4789 almacen-lumen
```

`GET /api/health` responde `{"status":"ok"}`. El Dockerfile vuelve a generar
el catálogo dentro de la imagen y usa esa ruta como healthcheck.

## Mapa del repositorio

| Ruta | Qué es |
| --- | --- |
| `app-tienda/` | Servidor y pantalla de la tienda |
| `datos/generar-datos.js` | Semilla fija, Faker y anonimización |
| `datos/dump-ficticio.json` | Volcado inventado, con correos y nombres |
| `datos/db.json` | Resultado del generador. El pipeline lo vuelve a crear |
| `e2e/` | Gherkin, Screenplay y pytest-bdd |
| `azure-pipelines.yml` | Stages y gates. Hay una copia en `pipeline/` |
| `pact/` | Contrato de `GET /api/productos` |
| `Dockerfile` | Imagen de la tienda |
| `docs/DOCUMENTO-SOPORTE.pdf` | Evidencia de las seis fases |

## Fase 1 — datos

`SEMILLA` vale `20261117` dentro de `datos/generar-datos.js`. El generador
arma 4 categorías y 24 productos con nombre, precio en MXN, stock y categoría
coherentes. `esc-05` queda con stock 1 y `esc-06` agotado, para los bordes.

Antes de escribir clientes lee `dump-ficticio.json` y enmascara nombre, correo,
teléfono y calle. Una prueba unitaria comprueba que ningún correo del volcado
aparece en el catálogo.

No se versionan datos generados en un pipeline de verdad porque el script y la
semilla ya los reproducen: meter `db.json` al git solo ensucia el diff. Este
repo igual lo trae, porque el reto pide el archivo resultante. Cada stage del
pipeline lo borra y lo regenera antes de probar.

## Fase 2 — gates

`azure-pipelines.yml` corre, en este orden: Build, SmokeTests, LoadTest, E2E,
Contract, CloudTests y Deploy. Deploy declara `dependsOn: LoadTest` y
`condition: succeeded()`. Si `pipeline/load-test.js` sale con 1, Deploy no corre.

| Gate | Dónde | Qué corta |
| --- | --- | --- |
| Build | stage Build | `npm test` o la imagen de Docker |
| Smoke | stage SmokeTests, `pipeline/smoke-test.js` | health, catálogo menor a 20, o pedido que no se crea |
| Carga | stage LoadTest | p95 ≥ 800 ms o error ≥ 1% |
| E2E | stage E2E | cualquier escenario de pytest |
| Contrato | stage Contract | el pact de `GET /api/productos` |
| Deploy | stage Deploy | no arranca si falló alguno de los anteriores |

La corrida verde y la roja de esta máquina están en
`docs/evidencias/load-green.json` y `load-red.json`. No hay organización de
Azure DevOps conectada: conectar el repo es demo guiada. En Azure Pipelines
se elige este repositorio y el YAML de la raíz.

## Fase 3 — del caso manual al automatizado

Los seis casos están escritos para Azure Test Plans en
`e2e/casos-azure-test-plans.md`. El Gherkin usa keywords en inglés y el texto
en español. El patrón Screenplay vive en `e2e/screenplay/` (Actor, BrowseTheWeb,
Tasks, Questions) y los pasos en `e2e/steps/pasos.py`.

El stage E2E publica `e2e/reports/junit.xml` con `PublishTestResults@2`. El
título del escenario es el vínculo con el caso manual.

Los dos bordes (stock de más y carrito vacío) salieron del prompt de
`docs/prompt-escenario-ia.md`. Este entorno no tiene el MCP de Playwright ni
una sesión de Claude; el prompt está guardado y los escenarios sí corren.

## Fase 4 — nube

`e2e/nube.py` arma el WebSocket de Sauce Labs
(`wss://usuario:clave@ondemand.<región>.saucelabs.com/playwright`) y las
capabilities. Si `SAUCE_USERNAME` y `SAUCE_ACCESS_KEY` están vacías, el stage
CloudTests ejecuta `e2e/comprobar_nube.py` y sale en 0. No hay cuenta de Sauce
en esta corrida.

Frente a local cambia la URL de la tienda (`BASE_URL`) y el browser: deja de
lanzarse en el agente y se conecta al grid. Los escenarios no cambian.

## Fase 5 — contenedor y contrato

La imagen corre como usuario `lumen`, genera el catálogo al construirla y
expone el puerto 4789. El healthcheck pega a `/api/health`.

El consumidor es `almacen-lumen-front` y el proveedor `almacen-lumen-api`.
El pact cubre `GET /api/productos` (id, nombre, precio, stock, categoría).
`npm run pact:consumer` lo escribe; `npm run pact:provider` lo verifica contra
la tienda encendida.

Partir el monolito hoy no conviene: catálogo, pedido y existencia caben en un
proceso y el tráfico de esta práctica no paga el costo de red. Si se partiera,
aparecerían tres contratos: catálogo (`GET /api/productos`, el que ya está),
pedidos (`POST /api/pedidos`) e inventario (la reserva de stock). El de
catálogo es el primero que habría que conservar.

## Fase 6 — métricas

Medidas en esta máquina, el 17 de noviembre de 2026. No salen de un tablero
de Azure. El lead time de un agente limpio de Azure sería más alto porque
instala Playwright.

| Métrica DORA | Lectura | De dónde sale |
| --- | --- | --- |
| Frecuencia de despliegue | Cada push a `main` que pasa los gates | El stage Deploy solo corre con `succeeded()` |
| Lead time | Unos 15 minutos de commit a imagen lista en un agente nuevo | Aquí, unitarias 0.2 s, humo y carga ~10 s, e2e 2.1 s, imagen ~8 s sin contar la descarga de Node |
| Tasa de fallo de cambios | 1 de 2 corridas de carga se rechazó a propósito | `load-red.json` tiene `passed: false` y no desplegaría |
| MTTR | Menos de 30 minutos, no cronometrado en producción | Volver al tag anterior de la imagen y reiniciar el contenedor |

La carga no es un piso de la pirámide: es un gate aparte.

```
        E2E  (6 escenarios Screenplay)
     Integración  (smoke + Pact)
  Unitarias  (anonimización, catálogo, pedidos)
```

Riesgos:

1. El p95 de un agente compartido se mueve. El SLA de 800 ms tiene margen
   (aquí el p95 fue 1.73 ms), pero hay que calentar el proceso y no apretar
   el umbral contra el ruido. El script ya descarta 20 peticiones de calentamiento.
2. El stock vive en memoria y se reinicia con el proceso. Un reinicio a media
   prueba descuenta de cero. Para una tienda real el stock iría a una base y
   el contrato incluiría la reserva.
3. Sauce y ACR no tienen credenciales. El pipeline no las inventa: las etapas
   avisan y siguen. Hay que cargarlas en un variable group, nunca en el repo.

## Qué corre de verdad y qué es demo

Corre de verdad: generador, anonimización, tienda, humo, carga en verde y en
rojo, seis escenarios Playwright, pact consumidor y proveedor, imagen Docker
con healthcheck en verde.

Demo guiada, sin portal: conectar GitHub a Azure Pipelines, Azure Test Plans,
Sauce Labs y publicar la imagen en Azure Container Registry. El YAML, las
capabilities y el mapeo de casos ya están listos para cuando existan las cuentas.

## API

| Método | Ruta | Uso |
| --- | --- | --- |
| GET | `/api/health` | La app encendió |
| GET | `/api/categorias` | 4 categorías |
| GET | `/api/productos` | Catálogo |
| POST | `/api/pedidos` | Crea un folio. 409 si no hay stock, 400 si el carrito va vacío |
| GET | `/api/pedidos` | Pedidos de este proceso |
