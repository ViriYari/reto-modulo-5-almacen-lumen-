# Casos manuales para Azure Test Plans

Keywords del Gherkin en inglés y texto en español. Cada caso manual se
automatiza con el escenario de la misma fila. El pipeline publica el JUnit
con `PublishTestResults@2`; el título del escenario es el vínculo.

| Id | Caso manual | Feature | Escenario |
| --- | --- | --- | --- |
| TC-CAT-01 | Abrir la tienda y comprobar que el catálogo trae el inventario | catalogo.feature | El catálogo muestra el inventario generado |
| TC-CAT-02 | Filtrar por Cerámica y ver solo esa categoría | catalogo.feature | Filtrar el catálogo por una categoría |
| TC-CAR-01 | Agregar una pieza disponible y ver el subtotal | carrito.feature | Agregar un producto disponible al carrito |
| TC-PED-01 | Confirmar el pedido y recibir folio | pedidos.feature | Confirmar un pedido con el carrito |
| TC-BOR-01 | Pedir más piezas de las que hay | bordes.feature | No se puede agregar más piezas que el stock |
| TC-BOR-02 | Confirmar sin piezas en el carrito | bordes.feature | No se confirma un pedido con el carrito vacío |

TC-BOR-01 y TC-BOR-02 salieron del prompt en `docs/prompt-escenario-ia.md`.

Pasos manuales de TC-PED-01, como quedarían en Test Plans:

1. Abrir la tienda.
2. Agregar 1 pieza del primer producto con existencia.
3. Escribir el nombre y un correo válido.
4. Confirmar el pedido.
5. Resultado esperado: aparece un folio que empieza con `LM-`.

Sin organización de Azure DevOps esta tabla es la evidencia del diseño. Crear
los casos en el portal y pegar el escenario en la descripción es demo guiada.
