"""Imprime el vínculo entre escenarios automatizados y los casos manuales.

Si existen AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT y
TEST_RUN_ID, deja el mapa listo para pegarlo en la corrida. Sin esos datos
no llama a Azure: la publicación real de JUnit la hace PublishTestResults@2.
"""

from pathlib import Path

MAPA = """
Casos manuales de Azure Test Plans y su escenario automatizado:
- TC-CAT-01 Catálogo visible          -> El catálogo muestra el inventario generado
- TC-CAT-02 Filtro por categoría      -> Filtrar el catálogo por una categoría
- TC-CAR-01 Agregar al carrito        -> Agregar un producto disponible al carrito
- TC-PED-01 Confirmar pedido          -> Confirmar un pedido con el carrito
- TC-BOR-01 Stock insuficiente (IA)   -> No se puede agregar más piezas que el stock
- TC-BOR-02 Carrito vacío (IA)        -> No se confirma un pedido con el carrito vacío
El JUnit de pytest (e2e/reports/junit.xml) usa el nombre del escenario,
así que el resultado se puede asociar al caso por ese título.
"""


def main() -> None:
    destino = Path("docs/evidencias")
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "test-plans.txt").write_text(MAPA.strip() + "\n", encoding="utf-8")
    print(MAPA)


if __name__ == "__main__":
    main()
