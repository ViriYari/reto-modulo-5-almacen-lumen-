Feature: Catálogo de la tienda
  Como cliente quiero ver los productos publicados
  para elegir qué llevarme.

  Scenario: El catálogo muestra el inventario generado
    Given un cliente abre la tienda
    When consulta los productos publicados
    Then ve al menos 20 productos
    And existen al menos 4 categorías

  Scenario: Filtrar el catálogo por una categoría
    Given un cliente abre la tienda
    When filtra el catálogo por "Cerámica"
    Then solo ve productos de "Cerámica"
    And ve al menos 1 producto
