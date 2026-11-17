"""Arma el PDF de soporte con las capturas reales de esta corrida."""

import json
from pathlib import Path

from fpdf import FPDF

RAIZ = Path(__file__).resolve().parents[1]
EVIDENCIA = RAIZ / "docs" / "evidencias"
SALIDA = RAIZ / "docs" / "DOCUMENTO-SOPORTE.pdf"
FUENTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FUENTE_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class Soporte(FPDF):
    def footer(self):
        self.set_y(-14)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, f"Almacén Lumen  ·  reto módulo 5  ·  {self.page_no()}", align="C")


def escribir(pdf, texto, alto):
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, alto, texto, new_x="LMARGIN", new_y="NEXT")


def parrafo(pdf, texto, alto=6):
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(20, 20, 20)
    escribir(pdf, texto, alto)
    pdf.ln(2)


def titulo(pdf, texto):
    pdf.ln(2)
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(31, 58, 52)
    escribir(pdf, texto, 8)
    pdf.ln(1)


def sub(pdf, texto):
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(31, 58, 52)
    escribir(pdf, texto, 7)
    pdf.ln(1)


def figura(pdf, nombre, pie):
    ruta = EVIDENCIA / nombre
    if not ruta.exists():
        parrafo(pdf, f"(Falta la captura {nombre}.)")
        return
    pdf.ln(1)
    pdf.image(str(ruta), w=174)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(80, 80, 80)
    escribir(pdf, pie, 5)
    pdf.ln(2)


def tabla(pdf, filas):
    pdf.set_font("DejaVu", "", 9)
    ancho = (40, 55, 79)
    for indice, fila in enumerate(filas):
        pdf.set_fill_color(31, 58, 52 if indice == 0 else 244)
        if indice == 0:
            pdf.set_text_color(246, 241, 230)
            pdf.set_font("DejaVu", "B", 9)
        else:
            pdf.set_text_color(20, 20, 20)
            pdf.set_font("DejaVu", "", 9)
        x = pdf.get_x()
        y = pdf.get_y()
        altos = []
        for celda, w in zip(fila, ancho):
            altos.append(pdf.multi_cell(w, 5, celda, border=0, dry_run=True, output="LINES", new_x="RIGHT", new_y="TOP"))
        alto = max(len(lineas) for lineas in altos) * 5 + 2
        if y + alto > 275:
            pdf.add_page()
            y = pdf.get_y()
        for celda, w in zip(fila, ancho):
            pdf.set_xy(x, y)
            pdf.multi_cell(w, 5, celda, border=1, fill=indice == 0, new_x="RIGHT", new_y="TOP")
            x += w
        pdf.set_xy(pdf.l_margin, y + alto)
    pdf.ln(3)


def main():
    verde = json.loads((EVIDENCIA / "load-green.json").read_text(encoding="utf-8"))
    rojo = json.loads((EVIDENCIA / "load-red.json").read_text(encoding="utf-8"))
    pdf = Soporte()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_font("DejaVu", "", FUENTE)
    pdf.add_font("DejaVu", "B", FUENTE_B)
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 20)
    pdf.set_text_color(31, 58, 52)
    escribir(pdf, "Documento de soporte", 10)
    pdf.set_font("DejaVu", "", 13)
    escribir(pdf, "Módulo 5 — QA Cloud-Native\nAlmacén Lumen", 7)
    pdf.ln(2)
    parrafo(
        pdf,
        "Tienda de práctica con catálogo reproducible, quality gates, escenarios "
        "Screenplay y un contrato Pact sobre GET /api/productos. Este PDF junta "
        "lo que se ejecutó en la máquina de la entrega. Donde no hubo cuenta de "
        "Azure o de Sauce Labs, se dice.",
    )

    titulo(pdf, "Declaración honesta")
    parrafo(
        pdf,
        "Corre de verdad: el generador con semilla 20261117, la anonimización del "
        "volcado ficticio, la tienda, el humo, la carga en verde y en rojo, los "
        "seis escenarios de Playwright, el pact (consumidor y proveedor) y la "
        "imagen Docker, cuyo healthcheck quedó healthy.",
    )
    parrafo(
        pdf,
        "Demo guiada, sin portal: conectar el repositorio a Azure Pipelines, "
        "crear los casos en Azure Test Plans, abrir Sauce Labs y publicar la "
        "imagen en Azure Container Registry. El YAML, el mapeo de casos y las "
        "capabilities ya están en el repositorio. El código vive en este proyecto; "
        "el enlace de GitHub aparece cuando se crea el repositorio desde el proyecto.",
    )

    titulo(pdf, "Fase 1 — Datos de prueba (10 pts)")
    parrafo(
        pdf,
        "datos/generar-datos.js fija la semilla 20261117 y usa Faker en español. "
        "Salen 4 categorías y 24 productos: nombre, detalle, precio en MXN, stock "
        "y categoría. Cerámica no se mezcla con cables. esc-05 queda con 1 pieza "
        "y esc-06 agotado.",
    )
    parrafo(
        pdf,
        "El reto extra parte de datos/dump-ficticio.json (nombres y correos "
        "inventados, dominio .test). Antes de escribir datos/db.json se enmascara "
        "el nombre (M*** S*** P***), el correo (m***@dominio), el teléfono "
        "(***5678) y la calle. Una prueba unitaria falla si algún correo del "
        "volcado sobrevive.",
    )
    parrafo(
        pdf,
        "No se versionan datos generados porque la semilla y el script ya los "
        "reconstruyen: el archivo en git solo produce diffs ruidosos y se puede "
        "desalinear del generador. El pipeline regenera db.json en cada stage. "
        "El archivo va en el repo porque el entregable lo pide, y al ser "
        "determinista solo cambia cuando cambia el generador.",
    )

    titulo(pdf, "Fase 2 — Pipeline y quality gates (15 pts)")
    parrafo(
        pdf,
        "azure-pipelines.yml (y la copia pipeline/azure-pipelines.yml) declara "
        "Build, SmokeTests, LoadTest, E2E, Contract, CloudTests y Deploy. "
        "Deploy depende de LoadTest y exige succeeded(). El script "
        "pipeline/load-test.js sale con código 1 si el p95 no cumple o si la "
        "tasa de error llega al 1%. Ese exit 1 es el que detiene el deploy.",
    )
    sub(pdf, "Dónde está cada gate")
    tabla(
        pdf,
        [
            ("Gate", "Stage", "Qué lo pone en rojo"),
            ("Build", "Build", "Falla npm test o docker build"),
            ("Humo", "SmokeTests", "Sin health, catálogo < 20 o pedido rechazado"),
            ("Carga", "LoadTest", "p95 >= 800 ms o error >= 1%"),
            ("E2E", "E2E", "Un escenario pytest en rojo"),
            ("Contrato", "Contract", "El pact no verifica"),
            ("Deploy", "Deploy", "No arranca si un gate anterior falló"),
        ],
    )
    parrafo(
        pdf,
        f"Corrida verde, SLA 800 ms: {verde['requests']} peticiones, "
        f"{verde['errors']} errores, p95 {verde['p95Ms']} ms, passed={str(verde['passed']).lower()}.",
    )
    figura(pdf, "load-green.png", "Figura 1. Gate de carga en verde. No es el portal de Azure: es la salida real del script que el stage LoadTest ejecuta.")
    parrafo(
        pdf,
        f"Corrida roja, el mismo tráfico con el SLA bajado a 1 ms: p95 {rojo['p95Ms']} ms, "
        f"0% de error, passed={str(rojo['passed']).lower()}. El proceso terminó con código 1.",
    )
    figura(pdf, "load-red.png", "Figura 2. Gate de carga en rojo. Se forzó bajando el SLA, no apagando la tienda.")

    titulo(pdf, "Fase 3 — Casos, Gherkin y Screenplay (20 pts)")
    parrafo(
        pdf,
        "Los casos manuales TC-CAT-01, TC-CAT-02, TC-CAR-01, TC-PED-01, TC-BOR-01 "
        "y TC-BOR-02 están en e2e/casos-azure-test-plans.md, con los pasos que "
        "irían a Azure Test Plans. El Gherkin está en e2e/features. Keywords en "
        "inglés, texto en español. Screenplay: Actor, la habilidad BrowseTheWeb, "
        "tareas (abrir, filtrar, agregar, confirmar) y preguntas (conteos, folio, aviso).",
    )
    parrafo(
        pdf,
        "pytest terminó 6 passed en 2.09 s. El pipeline publica el JUnit con "
        "PublishTestResults@2. El título del escenario es el puente al caso manual. "
        "Crear los work items en el portal de Test Plans es demo guiada.",
    )
    figura(pdf, "pytest.png", "Figura 3. Salida de pytest: seis escenarios en verde.")
    figura(pdf, "04-folio.png", "Figura 4. Camino feliz: folio de pedido después de confirmar el carrito.")
    parrafo(
        pdf,
        "Los dos bordes los pidió el prompt guardado en docs/prompt-escenario-ia.md. "
        "Este entorno no tiene servidor MCP de Playwright ni una sesión de Claude. "
        "El prompt se conservó y los escenarios se automatizaron y ejecutaron.",
    )
    figura(pdf, "05-stock.png", "Figura 5. Borde propuesto: 5 piezas de un producto con stock 1. El carrito sigue en 0.")
    figura(pdf, "06-carrito-vacio.png", "Figura 6. Segundo borde: confirmar sin piezas no crea folio.")

    titulo(pdf, "Fase 4 — Ejecución en la nube (10 pts)")
    parrafo(
        pdf,
        "e2e/nube.py prepara Chromium en Sauce Labs. La URL es "
        "wss://usuario:clave@ondemand.<región>.saucelabs.com/playwright, región "
        "us-west-1 por defecto, plataforma Windows 11. El stage CloudTests llama "
        "a e2e/comprobar_nube.py y, solo si hay SAUCE_USERNAME y SAUCE_ACCESS_KEY, "
        "lanza pytest contra el grid.",
    )
    parrafo(
        pdf,
        "Frente a local cambian dos cosas: BASE_URL deja de ser 127.0.0.1 y el "
        "browser deja de abrirse en el agente. Los features, los data-testid y "
        "el Screenplay se quedan igual. No hay cuenta de Sauce en esta entrega, "
        "así que no hay captura de dashboard. La evidencia es el código y "
        "docs/evidencias/sauce-capabilities.json.",
    )

    titulo(pdf, "Fase 5 — Contenedor y contrato (15 pts)")
    parrafo(
        pdf,
        "El Dockerfile parte de node:22-alpine, instala solo la dependencia de "
        "producción, corre el generador, cambia al usuario lumen y expone el "
        "4789. El healthcheck pide /api/health y exige status ok. La imagen "
        "almacen-lumen:reto5 se construyó y el contenedor publicó el puerto 4791. "
        "Respondió 24 productos, el primero cer-01, y el healthcheck pasó a healthy. "
        "La evidencia de texto está en docs/evidencias/docker.txt.",
    )
    parrafo(
        pdf,
        "Publicar en Azure Container Registry (az acr build) está en el stage "
        "Deploy y no se ejecutó: no hay ACR_NAME. Es demo guiada.",
    )
    parrafo(
        pdf,
        "Pact: el consumidor almacen-lumen-front describe GET /api/productos y el "
        "proveedor almacen-lumen-api lo verifica. La verificación de esta corrida "
        "dice Verification successful (docs/evidencias/pact.txt). El archivo del "
        "contrato queda en pact/pacts/.",
    )
    parrafo(
        pdf,
        "No conviene partir el monolito todavía. Catálogo, pantalla y pedidos "
        "comparten un proceso y no hay un equipo ni un tráfico que justifique el "
        "salto de red. Si se partiera, el primer contrato ya existe (GET "
        "/api/productos). Aparecerían además el de pedidos (POST /api/pedidos, "
        "con 400 y 409) y el de inventario (quién descuenta el stock).",
    )

    titulo(pdf, "Fase 6 — Métricas y estrategia (20 pts)")
    sub(pdf, "DORA")
    tabla(
        pdf,
        [
            ("Métrica", "Lectura", "Base"),
            ("Frecuencia de despliegue", "Cada push a main que pasa los gates", "Deploy solo corre con succeeded()"),
            ("Lead time", "Unos 15 min en un agente nuevo", "Aquí: unitarias 0.2 s, carga ~10 s, e2e 2.1 s, imagen ~8 s"),
            ("Tasa de fallo de cambios", "1 de 2 cargas rechazada a propósito", "load-red.json passed=false y no despliega"),
            ("MTTR", "< 30 min, no medido en producción", "Reactivar el tag anterior de la imagen"),
        ],
    )
    sub(pdf, "Pirámide")
    parrafo(
        pdf,
        "Abajo, muchas y rápidas: pruebas unitarias de anonimización, del catálogo "
        "reproducible y de las reglas de pedido (stock, correo, carrito vacío). "
        "En medio: el humo HTTP y el pact de GET /api/productos. Arriba, pocos: "
        "los 6 escenarios que abren el browser. La prueba de carga no es un piso; "
        "es el gate que decide si Deploy corre. El diagrama está en docs/piramide.svg.",
    )
    sub(pdf, "Riesgos y mitigación")
    parrafo(
        pdf,
        "1. El p95 de un agente compartido se mueve y puede poner el gate en rojo "
        "sin un defecto de la tienda. Mitigación: 20 peticiones de calentamiento "
        "(ya están) y un SLA con margen. Aquí el p95 fue 1.73 ms contra un límite "
        "de 800 ms.",
    )
    parrafo(
        pdf,
        "2. El stock vive en la memoria del proceso. Un reinicio lo devuelve al "
        "db.json y una prueba a medias no ve lo que otra ya compró. Mitigación: "
        "en una tienda real, persistir la existencia y ampliar el contrato con la "
        "reserva. En esta práctica el generador vuelve a dejar el mismo inventario.",
    )
    parrafo(
        pdf,
        "3. Sauce Labs y ACR dependen de secretos que no están. Si alguien los "
        "pega en el YAML, se filtran. Mitigación: variable group de Azure, "
        "valores vacíos por defecto y el stage en modo demo cuando faltan. "
        ".env.example documenta los nombres y no trae valores.",
    )

    titulo(pdf, "Checklist")
    parrafo(
        pdf,
        "Fase 1: datos/generar-datos.js y datos/db.json. Fase 2: azure-pipelines.yml "
        "y las dos capturas de carga. Fase 3: e2e/features, e2e/steps, pytest en "
        "verde y el prompt del borde. Fase 4: e2e/nube.py y sauce-capabilities.json. "
        "Fase 5: Dockerfile, contenedor healthy y pact verificado. Fase 6: esta "
        "tabla, la pirámide y los tres riesgos. El README explica cómo repetir cada paso.",
    )

    pdf.output(str(SALIDA))
    print(SALIDA)


if __name__ == "__main__":
    main()
