"""Arma el PDF de soporte con las capturas recortadas de esta corrida."""

import json
from pathlib import Path

from fpdf import FPDF
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIA = RAIZ / "docs" / "evidencias"
SALIDA = RAIZ / "docs" / "DOCUMENTO-SOPORTE.pdf"
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FUENTE_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class Soporte(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, f"Almacén Lumen  ·  documento de soporte  ·  {self.page_no()}", align="C")


def escribir(pdf, texto, alto, fuente=11, negrita=False, color=(28, 25, 21)):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B" if negrita else "", fuente)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, alto, texto, align="L", new_x="LMARGIN", new_y="NEXT")


def titulo(pdf, texto):
    pdf.ln(3)
    escribir(pdf, texto, 8, fuente=15, negrita=True, color=(31, 58, 52))
    pdf.ln(1)


def parrafo(pdf, texto):
    escribir(pdf, texto, 5.4, fuente=10.5)
    pdf.ln(1.5)


def recortar_terminal(ruta):
    imagen = Image.open(ruta).convert("RGB")
    pixeles = imagen.load()
    ancho, alto = imagen.size

    def fila_con_texto(y):
        return any(sum(pixeles[x, y]) > 140 for x in range(0, ancho, 4))

    arriba = next(y for y in range(alto) if fila_con_texto(y))
    abajo = next(y for y in range(alto - 1, -1, -1) if fila_con_texto(y))
    return imagen.crop((12, max(0, arriba - 18), ancho - 12, min(alto, abajo + 22)))


def cabe(pdf, alto):
    if pdf.get_y() + alto > pdf.h - 16:
        pdf.add_page()


def figura(pdf, imagen, pie, ancho=174, alto_max=92):
    proporcion = imagen.height / imagen.width
    alto = ancho * proporcion
    if alto > alto_max:
        corte = int(imagen.width * (alto_max / ancho))
        imagen = imagen.crop((0, 0, imagen.width, min(imagen.height, corte)))
        alto = alto_max
    cabe(pdf, alto + 12)
    pdf.set_x(pdf.l_margin)
    pdf.image(imagen, w=ancho, h=alto)
    pdf.ln(1)
    escribir(pdf, pie, 4.4, fuente=8.5, color=(90, 84, 74))
    pdf.ln(2)


def tabla(pdf, filas, anchos):
    for indice, fila in enumerate(filas):
        pdf.set_font("DejaVu", "B" if indice == 0 else "", 8.5)
        medidas = [
            pdf.multi_cell(ancho, 4.4, texto, dry_run=True, output="LINES", align="L")
            for texto, ancho in zip(fila, anchos)
        ]
        alto = max(len(lineas) for lineas in medidas) * 4.4 + 2.2
        cabe(pdf, alto)
        y = pdf.get_y()
        x = pdf.l_margin
        if indice == 0:
            pdf.set_fill_color(31, 58, 52)
            pdf.set_text_color(246, 241, 230)
        else:
            pdf.set_fill_color(255, 253, 248)
            pdf.set_text_color(28, 25, 21)
        for texto, ancho in zip(fila, anchos):
            pdf.set_xy(x, y)
            pdf.multi_cell(
                ancho,
                4.4,
                texto,
                border=1,
                fill=True,
                align="L",
                new_x="RIGHT",
                new_y="TOP",
            )
            x += ancho
        pdf.set_xy(pdf.l_margin, y + alto)
    pdf.ln(2)


def lamina(titulo, lineas):
    from PIL import ImageDraw, ImageFont

    imagen = Image.new("RGB", (1100, 64 + 34 * len(lineas)), (28, 25, 21))
    draw = ImageDraw.Draw(imagen)
    titulo_fuente = ImageFont.truetype(FUENTE_B, 26)
    cuerpo = ImageFont.truetype(FUENTE, 22)
    draw.text((24, 16), titulo, font=titulo_fuente, fill=(244, 239, 228))
    y = 58
    for linea in lineas:
        draw.text((24, y), linea, font=cuerpo, fill=(232, 224, 208))
        y += 34
    return imagen


def piramide():
    from PIL import ImageDraw, ImageFont

    imagen = Image.new("RGB", (980, 300), (244, 239, 228))
    draw = ImageDraw.Draw(imagen)
    fuente = ImageFont.truetype(FUENTE, 22)
    titulo_fuente = ImageFont.truetype(FUENTE_B, 26)
    draw.text((28, 16), "Pirámide de pruebas", font=titulo_fuente, fill=(28, 25, 21))
    niveles = [
        (120, (31, 58, 52), "E2E · 6 escenarios"),
        (220, (47, 86, 76), "Integración · smoke y Pact"),
        (340, (184, 90, 50), "Unitarias · datos y pedidos"),
    ]
    centro = 250
    for indice, (ancho, color, etiqueta) in enumerate(niveles):
        arriba = 70 + indice * 70
        draw.polygon(
            [
                (centro - ancho // 2, arriba + 58),
                (centro + ancho // 2, arriba + 58),
                (centro + ancho // 2 - 28, arriba),
                (centro - ancho // 2 + 28, arriba),
            ],
            fill=color,
        )
        draw.text((centro + ancho // 2 + 24, arriba + 16), etiqueta, font=fuente, fill=(28, 25, 21))
    return imagen


def main():
    verde = json.loads((EVIDENCIA / "load-green.json").read_text(encoding="utf-8"))
    rojo = json.loads((EVIDENCIA / "load-red.json").read_text(encoding="utf-8"))
    pdf = Soporte(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(18, 16, 18)
    pdf.add_font("DejaVu", "", FUENTE)
    pdf.add_font("DejaVu", "B", FUENTE_B)
    pdf.add_page()

    escribir(pdf, "Documento de soporte", 9, fuente=20, negrita=True, color=(31, 58, 52))
    escribir(pdf, "Módulo 5 — QA Cloud-Native", 6, fuente=12, color=(31, 58, 52))
    escribir(pdf, "Almacén Lumen", 6, fuente=12)
    pdf.ln(2)
    parrafo(
        pdf,
        "Tienda de práctica con catálogo reproducible, quality gates, escenarios "
        "Screenplay y un contrato Pact de GET /api/productos. Este PDF junta lo que "
        "se ejecutó. Donde no hubo cuenta de Azure o de Sauce Labs, se dice.",
    )

    titulo(pdf, "Declaración honesta")
    parrafo(
        pdf,
        "Corre de verdad: el generador con semilla 20261117, la anonimización del "
        "volcado ficticio, la tienda, el humo, la carga en verde y en rojo, los seis "
        "escenarios de Playwright, el pact del consumidor y del proveedor, y la imagen "
        "Docker con healthcheck healthy.",
    )
    parrafo(
        pdf,
        "Demo guiada, sin portal: conectar el repositorio a Azure Pipelines, crear los "
        "casos en Azure Test Plans, abrir Sauce Labs y publicar la imagen en Azure "
        "Container Registry. El YAML, el mapeo de casos y las capabilities ya están en "
        "el repositorio. El enlace de GitHub aparece cuando se crea el repositorio del proyecto.",
    )

    titulo(pdf, "Fase 1 — Datos de prueba (10 pts)")
    parrafo(
        pdf,
        "datos/generar-datos.js fija la semilla 20261117 y usa Faker en español. "
        "Salen 4 categorías y 24 productos, con nombre, detalle, precio en MXN, stock "
        "y categoría. Cerámica no se mezcla con cables. esc-05 queda con 1 pieza y "
        "esc-06 queda agotado, para los casos de borde.",
    )
    parrafo(
        pdf,
        "El reto extra parte de datos/dump-ficticio.json. Los nombres y correos son "
        "inventados y usan el dominio .test. Antes de escribir datos/db.json se "
        "enmascara el nombre (M*** S*** P***), el correo (m***@dominio), el teléfono "
        "(***5678) y la calle. Una prueba unitaria falla si algún correo del volcado sobrevive.",
    )
    parrafo(
        pdf,
        "En un pipeline no se versionan los datos generados: la semilla y el script "
        "ya los reconstruyen, y el archivo en git solo ensucia el diff. Cada stage "
        "regenera db.json. El archivo va en el repositorio porque el entregable lo pide "
        "y, al ser determinista, solo cambia cuando cambia el generador.",
    )
    figura(
        pdf,
        Image.open(EVIDENCIA / "03-carrito.png").convert("RGB"),
        "Figura 1. Catálogo de la tienda. 24 piezas, cuatro categorías y el carrito a la derecha.",
        alto_max=78,
    )

    titulo(pdf, "Fase 2 — Pipeline y quality gates (15 pts)")
    parrafo(
        pdf,
        "azure-pipelines.yml, copiado también en pipeline/azure-pipelines.yml, declara "
        "Build, SmokeTests, LoadTest, E2E, Contract, CloudTests y Deploy. Deploy depende "
        "de LoadTest y exige succeeded(). pipeline/load-test.js sale con código 1 si el "
        "p95 no cumple o si el error llega al 1%. Ese código detiene el deploy.",
    )
    tabla(
        pdf,
        [
            ("Gate", "Stage", "Qué lo pone en rojo"),
            ("Build", "Build", "Falla npm test o docker build"),
            ("Humo", "SmokeTests", "Sin health, catálogo corto o pedido rechazado"),
            ("Carga", "LoadTest", "p95 de 800 ms o más, o error de 1% o más"),
            ("E2E", "E2E", "Un escenario de pytest en rojo"),
            ("Contrato", "Contract", "El pact no verifica"),
            ("Deploy", "Deploy", "No arranca si un gate anterior falló"),
        ],
        (32, 36, 106),
    )
    parrafo(
        pdf,
        f"Corrida verde, SLA de 800 ms: {verde['requests']} peticiones, "
        f"{verde['errors']} errores, p95 de {verde['p95Ms']} ms, passed true.",
    )
    figura(
        pdf,
        recortar_terminal(EVIDENCIA / "load-green.png"),
        "Figura 2. Gate de carga en verde. Es la salida del script que corre el stage LoadTest, no el portal de Azure.",
        alto_max=62,
    )
    parrafo(
        pdf,
        f"Corrida roja, el mismo tráfico con el SLA bajado a 1 ms: p95 de {rojo['p95Ms']} ms, "
        "0% de error, passed false. El proceso terminó con código 1.",
    )
    figura(
        pdf,
        recortar_terminal(EVIDENCIA / "load-red.png"),
        "Figura 3. Gate de carga en rojo. Se forzó bajando el SLA, con la tienda encendida.",
        alto_max=62,
    )

    titulo(pdf, "Fase 3 — Casos, Gherkin y Screenplay (20 pts)")
    parrafo(
        pdf,
        "Los casos manuales TC-CAT-01, TC-CAT-02, TC-CAR-01, TC-PED-01, TC-BOR-01 y "
        "TC-BOR-02 están en e2e/casos-azure-test-plans.md. El Gherkin vive en e2e/features: "
        "keywords en inglés y texto en español. Screenplay separa Actor, la habilidad "
        "BrowseTheWeb, las tareas (abrir, filtrar, agregar, confirmar) y las preguntas "
        "(conteos, folio, aviso).",
    )
    parrafo(
        pdf,
        "pytest terminó 6 passed en 2.09 s. El pipeline publica el JUnit con "
        "PublishTestResults@2 y el título del escenario enlaza el caso manual. Crear "
        "los work items en el portal de Test Plans es demo guiada.",
    )
    figura(
        pdf,
        lamina("pytest — seis escenarios en verde", ["......", "6 passed in 2.09s"]),
        "Figura 4. Salida de pytest: seis escenarios en verde.",
        alto_max=36,
    )
    figura(
        pdf,
        Image.open(EVIDENCIA / "04-folio.png").convert("RGB"),
        "Figura 5. Camino feliz. El pedido queda confirmado con folio LM-1002.",
        alto_max=112,
    )
    parrafo(
        pdf,
        "Los dos bordes salen del prompt guardado en docs/prompt-escenario-ia.md. "
        "Este entorno no tiene el servidor MCP de Playwright ni una sesión de Claude. "
        "El prompt se conservó y los escenarios se automatizaron y se ejecutaron.",
    )
    figura(
        pdf,
        Image.open(EVIDENCIA / "05-stock.png").convert("RGB"),
        "Figura 6. Borde propuesto: 5 piezas de un producto con stock 1. El carrito sigue en 0.",
        alto_max=78,
    )
    figura(
        pdf,
        Image.open(EVIDENCIA / "06-carrito-vacio.png").convert("RGB"),
        "Figura 7. Segundo borde: confirmar sin piezas no crea folio.",
        alto_max=78,
    )

    titulo(pdf, "Fase 4 — Ejecución en la nube (10 pts)")
    parrafo(
        pdf,
        "e2e/nube.py prepara Chromium en Sauce Labs. La conexión es un WebSocket a "
        "ondemand.REGION.saucelabs.com/playwright. La región por defecto es us-west-1 "
        "y la plataforma es Windows 11. El stage CloudTests llama a e2e/comprobar_nube.py "
        "y solo lanza pytest en el grid si existen SAUCE_USERNAME y SAUCE_ACCESS_KEY.",
    )
    parrafo(
        pdf,
        "Frente a local cambian dos cosas: BASE_URL deja de ser la máquina del agente "
        "y el browser deja de abrirse ahí. Los features, los data-testid y el Screenplay "
        "siguen igual. No hay cuenta de Sauce en esta entrega, así que no hay captura "
        "del dashboard. La evidencia es el código y docs/evidencias/sauce-capabilities.json.",
    )

    titulo(pdf, "Fase 5 — Contenedor y contrato (15 pts)")
    parrafo(
        pdf,
        "El Dockerfile parte de node:22-alpine, instala solo la dependencia de producción, "
        "vuelve a generar el catálogo, cambia al usuario lumen y expone el puerto 4789. "
        "El healthcheck pide /api/health y exige status ok. La imagen almacen-lumen:reto5 "
        "se construyó, el contenedor respondió 24 productos (el primero, cer-01) y el "
        "healthcheck pasó a healthy. El texto está en docs/evidencias/docker.txt.",
    )
    parrafo(
        pdf,
        "Publicar en Azure Container Registry queda en el stage Deploy y no se ejecutó: "
        "no hay ACR_NAME. Es demo guiada.",
    )
    parrafo(
        pdf,
        "Pact: el consumidor almacen-lumen-front describe GET /api/productos y el "
        "proveedor almacen-lumen-api lo verifica. Esta corrida terminó en Verification "
        "successful (docs/evidencias/pact.txt). El contrato queda en pact/pacts/.",
    )
    parrafo(
        pdf,
        "No conviene partir el monolito todavía. Catálogo, pantalla y pedidos comparten "
        "un proceso, y no hay un equipo ni un tráfico que pague el salto de red. Si se "
        "partiera, el primer contrato ya existe: GET /api/productos. Aparecerían además "
        "el de pedidos (POST /api/pedidos, con 400 y 409) y el de inventario, que es quien "
        "descuenta el stock.",
    )

    pdf.add_page()
    titulo(pdf, "Fase 6 — Métricas y estrategia (20 pts)")
    escribir(pdf, "DORA", 6, fuente=12, negrita=True, color=(31, 58, 52))
    pdf.ln(1)
    tabla(
        pdf,
        [
            ("Métrica", "Lectura", "Base"),
            ("Frecuencia de despliegue", "Cada push a main que pasa los gates", "Deploy solo corre con succeeded()"),
            ("Lead time", "Unos 15 min en un agente nuevo", "Aquí: unitarias 0.2 s, carga 10 s, e2e 2.1 s, imagen 8 s"),
            ("Fallo de cambios", "1 de 2 cargas rechazada a propósito", "load-red.json tiene passed false y no despliega"),
            ("MTTR", "Menos de 30 min, sin incidente real", "Volver al tag anterior de la imagen"),
        ],
        (48, 62, 64),
    )
    parrafo(
        pdf,
        "Abajo hay muchas pruebas rápidas: anonimización, catálogo reproducible y reglas "
        "de pedido. En medio están el humo HTTP y el pact. Arriba están los 6 escenarios "
        "que abren el browser. La carga no es un piso de la pirámide: es el gate que "
        "decide si Deploy corre.",
    )
    figura(pdf, piramide(), "Figura 8. Dónde cae cada herramienta.", alto_max=62)
    escribir(pdf, "Riesgos y mitigación", 6, fuente=12, negrita=True, color=(31, 58, 52))
    pdf.ln(1)
    parrafo(
        pdf,
        "1. El p95 de un agente compartido se mueve y puede poner el gate en rojo sin "
        "un defecto de la tienda. Mitigación: 20 peticiones de calentamiento, que ya "
        "están, y un SLA con margen. Aquí el p95 fue 1.73 ms contra un límite de 800 ms.",
    )
    parrafo(
        pdf,
        "2. El stock vive en la memoria del proceso. Un reinicio lo devuelve al db.json "
        "y una prueba a medias no ve lo que otra ya compró. Mitigación: en una tienda "
        "real, persistir la existencia y ampliar el contrato con la reserva. Aquí el "
        "generador vuelve a dejar el mismo inventario.",
    )
    parrafo(
        pdf,
        "3. Sauce Labs y el registro de contenedores dependen de secretos que no están. "
        "Si alguien los pega en el YAML, se filtran. Mitigación: un variable group de "
        "Azure, valores vacíos por defecto y la etapa en modo demo cuando faltan. "
        ".env.example documenta los nombres y no trae valores.",
    )

    titulo(pdf, "Checklist")
    parrafo(
        pdf,
        "Fase 1: datos/generar-datos.js y datos/db.json. Fase 2: azure-pipelines.yml y "
        "las figuras 2 y 3. Fase 3: e2e/features, e2e/steps, pytest en verde y el prompt "
        "del borde. Fase 4: e2e/nube.py y sauce-capabilities.json. Fase 5: Dockerfile, "
        "contenedor healthy y pact verificado. Fase 6: la tabla DORA, la pirámide y los "
        "tres riesgos. El README explica cómo repetir cada paso.",
    )

    pdf.output(str(SALIDA))
    print(SALIDA)


if __name__ == "__main__":
    main()
