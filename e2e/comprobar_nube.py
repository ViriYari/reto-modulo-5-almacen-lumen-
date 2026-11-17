"""Revisa que la ejecución remota esté cableada. No abre Sauce Labs."""

import json
from pathlib import Path

from nube import CAPACIDADES

CAMBIOS = """
Qué cambia frente a local:
- BASE_URL apunta a la tienda publicada, no a http://127.0.0.1:4789.
- El browser deja de lanzarse en la máquina del pipeline y se conecta por
  WebSocket a ondemand.<región>.saucelabs.com/playwright.
- Hacen falta SAUCE_USERNAME y SAUCE_ACCESS_KEY. El resto de los escenarios,
  los data-testid y el Screenplay no cambian.
- Sin esas variables este script termina en 0 y el stage queda como demo guiada.
"""


def main() -> None:
    destino = Path("docs/evidencias")
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "sauce-capabilities.json").write_text(
        json.dumps(CAPACIDADES, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(CAPACIDADES, indent=2, ensure_ascii=False))
    print(CAMBIOS)


if __name__ == "__main__":
    main()
