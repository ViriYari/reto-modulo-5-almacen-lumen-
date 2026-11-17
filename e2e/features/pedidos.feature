Feature: Pedidos
  Como cliente quiero confirmar lo que llevo en el carrito.

  Scenario: Confirmar un pedido con el carrito
    Given un cliente abre la tienda
    When agrega 1 pieza del primer producto con stock suficiente
    And confirma el pedido a nombre de "Cliente Demo" con correo "cliente.demo@example.com"
    Then recibe un folio de pedido
