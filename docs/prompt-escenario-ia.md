# Prompt usado para los casos de borde

Este entorno no tiene el servidor MCP de Playwright ni una sesión de Claude.
El prompt de abajo es el que se usó para proponer los escenarios, y el
resultado está automatizado en `e2e/features/bordes.feature`. Los dos casos
corren de verdad con pytest.

```
Eres un QA. La tienda Almacén Lumen corre en BASE_URL.
El catálogo tiene productos con data-testid="product-card", data-stock y data-product-id.
Hay un producto con stock 1 (data-product-id="esc-05") y otro agotado ("esc-06").
El carrito está en data-testid="cart-count" y el checkout en data-testid="checkout-submit".
Los avisos salen en data-testid="aviso" con data-tipo="stock" o data-tipo="vacio".

Propón 2 escenarios de borde en Gherkin (keywords en inglés, texto en español)
que no dupliquen el camino feliz de catálogo, carrito y pedido:
1. Intentar agregar más piezas que el stock.
2. Confirmar un pedido con el carrito vacío.

Luego automatízalos con el patrón Screenplay (Tasks y Questions) y pytest-bdd,
usando los data-testid, sin selectores CSS frágiles de clases.
```
