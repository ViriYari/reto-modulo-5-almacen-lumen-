Feature: Carrito de compras
  Como cliente quiero juntar piezas antes de pagar.

  Scenario: Agregar un producto disponible al carrito
    Given un cliente abre la tienda
    When agrega 1 pieza del primer producto con stock suficiente
    Then el contador del carrito es 1
    And el subtotal del carrito es mayor a 0
