"""Recorre la tienda y guarda las capturas que van al documento de soporte."""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "docs" / "evidencias"
BASE = "http://127.0.0.1:4789"


def pagina_de_texto(ruta_txt: Path, titulo: str) -> Path:
    html = SALIDA / f"{ruta_txt.stem}.html"
    cuerpo = ruta_txt.read_text(encoding="utf-8") if ruta_txt.exists() else "(sin salida)"
    html.write_text(
        f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>{titulo}</title>
<style>
  body {{ margin: 0; background: #1c1915; color: #f4efe4; font: 15px/1.45 "DejaVu Sans Mono", monospace; }}
  h1 {{ font-family: Georgia, serif; font-weight: 500; padding: 28px 32px 0; }}
  pre {{ white-space: pre-wrap; padding: 12px 32px 40px; }}
</style></head>
<body><h1>{titulo}</h1><pre>{cuerpo.replace("&", "&amp;").replace("<", "&lt;")}</pre></body></html>
""",
        encoding="utf-8",
    )
    return html


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        contexto = navegador.new_context(viewport={"width": 1360, "height": 900}, locale="es-MX")
        pagina = contexto.new_page()
        pagina.goto(BASE)
        pagina.locator("[data-testid='product-card']").first.wait_for()
        pagina.screenshot(path=str(SALIDA / "01-catalogo.png"), full_page=True)

        pagina.get_by_role("button", name="Cerámica", exact=True).click()
        pagina.screenshot(path=str(SALIDA / "02-filtro-ceramica.png"))

        pagina.get_by_role("button", name="Todas", exact=True).click()
        tarjeta = pagina.locator("[data-testid='product-card'][data-product-id='cer-01']")
        tarjeta.locator("[data-testid='add-to-cart']").click()
        pagina.locator("[data-testid='cart-count']").wait_for()
        pagina.screenshot(path=str(SALIDA / "03-carrito.png"))

        pagina.locator("[data-testid='checkout-nombre']").fill("Cliente Demo")
        pagina.locator("[data-testid='checkout-correo']").fill("cliente.demo@example.com")
        pagina.locator("[data-testid='checkout-submit']").click()
        pagina.locator("[data-testid='order-folio']").wait_for()
        pagina.screenshot(path=str(SALIDA / "04-folio.png"))

        borde = contexto.new_page()
        borde.goto(BASE)
        borde.locator("[data-product-id='esc-05']").wait_for()
        borde.locator("[data-product-id='esc-05'] [data-testid='qty']").fill("5")
        borde.locator("[data-product-id='esc-05'] [data-testid='add-to-cart']").click()
        aviso = borde.locator("[data-testid='aviso'][data-tipo='stock']")
        aviso.wait_for()
        aviso.scroll_into_view_if_needed()
        borde.screenshot(path=str(SALIDA / "05-stock.png"))

        vacio = contexto.new_page()
        vacio.goto(BASE)
        vacio.locator("[data-testid='product-card']").first.wait_for()
        vacio.locator("[data-testid='checkout-submit']").click()
        aviso_vacio = vacio.locator("[data-testid='aviso'][data-tipo='vacio']")
        aviso_vacio.wait_for()
        aviso_vacio.scroll_into_view_if_needed()
        vacio.screenshot(path=str(SALIDA / "06-carrito-vacio.png"))

        movil = navegador.new_context(viewport={"width": 390, "height": 844}, locale="es-MX")
        movil_pagina = movil.new_page()
        movil_pagina.goto(BASE)
        movil_pagina.locator("[data-testid='product-card']").first.wait_for()
        movil_pagina.screenshot(path=str(SALIDA / "07-movil.png"), full_page=True)
        movil.close()

        for nombre, titulo in (
            ("load-green.json", "Quality gate de carga en verde"),
            ("load-red.json", "Quality gate de carga en rojo"),
            ("pytest.txt", "pytest — seis escenarios en verde"),
        ):
            html = pagina_de_texto(SALIDA / nombre, titulo)
            pagina.goto(html.as_uri())
            pagina.screenshot(path=str(SALIDA / f"{Path(nombre).stem}.png"))

        navegador.close()

    verde = json.loads((SALIDA / "load-green.json").read_text(encoding="utf-8"))
    rojo = json.loads((SALIDA / "load-red.json").read_text(encoding="utf-8"))
    print(f"capturas en {SALIDA}")
    print(f"verde passed={verde['passed']} p95={verde['p95Ms']}")
    print(f"rojo passed={rojo['passed']} p95={rojo['p95Ms']}")


if __name__ == "__main__":
    main()
