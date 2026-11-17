import os

from playwright.sync_api import sync_playwright


CAPACIDADES = {
    "browserName": "chromium",
    "browserVersion": "latest",
    "platformName": "Windows 11",
    "sauce:options": {
        "name": "Almacén Lumen — catálogo, carrito y pedidos",
        "build": "reto-modulo-5",
        "screenResolution": "1920x1080",
    },
}


def endpoint() -> str:
    usuario = os.environ["SAUCE_USERNAME"]
    clave = os.environ["SAUCE_ACCESS_KEY"]
    region = os.environ.get("SAUCE_REGION", "us-west-1")
    return f"wss://{usuario}:{clave}@ondemand.{region}.saucelabs.com/playwright"


def conectar():
    """Abre Chromium en Sauce Labs. Solo se llama si hay credenciales."""
    playwright = sync_playwright().start()
    return playwright.chromium.connect(endpoint())
