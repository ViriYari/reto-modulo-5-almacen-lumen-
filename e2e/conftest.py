import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
pytest_plugins = ["steps.pasos"]

from screenplay.abilities import BrowseTheWeb
from screenplay.actor import Actor

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("BASE_URL", "http://127.0.0.1:4789")


def _sana() -> bool:
    try:
        with urllib.request.urlopen(f"{BASE}/api/health", timeout=1) as respuesta:
            cuerpo = json.load(respuesta)
            return respuesta.status == 200 and cuerpo.get("status") == "ok"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return False


@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}


@pytest.fixture(scope="session", autouse=True)
def tienda():
    if os.environ.get("SAUCE_USERNAME") and os.environ.get("BASE_URL_NUBE"):
        yield
        return
    if _sana():
        yield
        return
    env = {**os.environ, "PORT": "4789"}
    proceso = subprocess.Popen(
        ["node", "app-tienda/server.js"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    limite = time.time() + 20
    while time.time() < limite:
        if proceso.poll() is not None:
            salida = proceso.stdout.read() if proceso.stdout else ""
            raise RuntimeError(f"la tienda no arrancó\n{salida}")
        if _sana():
            break
        time.sleep(0.3)
    else:
        proceso.terminate()
        raise RuntimeError("health check agotó el tiempo")
    yield
    proceso.terminate()
    try:
        proceso.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proceso.kill()


@pytest.fixture
def page(browser):
    if os.environ.get("SAUCE_USERNAME") and os.environ.get("SAUCE_ACCESS_KEY"):
        from nube import conectar

        remoto = conectar()
        contexto = remoto.new_context(viewport={"width": 1360, "height": 900}, locale="es-MX")
        pagina = contexto.new_page()
        yield pagina
        contexto.close()
        remoto.close()
        return
    contexto = browser.new_context(viewport={"width": 1360, "height": 900}, locale="es-MX")
    pagina = contexto.new_page()
    yield pagina
    contexto.close()


@pytest.fixture
def cliente(page, base_url):
    return Actor.named("Cliente").who_can(BrowseTheWeb.using(page, base_url or BASE))


def pytest_configure(config):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
