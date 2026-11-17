Feature: Casos de borde del pedido
  Escenarios propuestos a partir del prompt de docs/prompt-escenario-ia.md.

  Scenario: No se puede agregar más piezas que el stock
    Given un cliente abre la tienda
    When intenta agregar 5 piezas de un producto con stock 1
    Then ve el aviso de stock insuficiente
    And el contador del carrito es 0

  Scenario: No se confirma un pedido con el carrito vacío
    Given un cliente abre la tienda
    When intenta confirmar un pedido sin productos
    Then ve el aviso de carrito vacío
    And no recibe un folio de pedido
