from pytest_bdd import given, parsers, then, when

from screenplay.questions import (
    AvisoVisible,
    CategoriasDelFiltro,
    ContadorDelCarrito,
    FolioDelPedido,
    NombresDeCategoriaVisibles,
    ProductosVisibles,
    SubtotalDelCarrito,
)
from screenplay.tasks import (
    AbrirLaTienda,
    AgregarMasQueElStock,
    AgregarProductoConStock,
    ConfirmarPedido,
    ConsultarProductos,
    FiltrarPorCategoria,
    IntentarPedidoVacio,
)


@given("un cliente abre la tienda")
def abre_la_tienda(cliente):
    cliente.attempts_to(AbrirLaTienda())


@when("consulta los productos publicados")
def consulta(cliente):
    cliente.attempts_to(ConsultarProductos())


@when(parsers.parse('filtra el catálogo por "{categoria}"'))
def filtra(cliente, categoria):
    cliente.attempts_to(FiltrarPorCategoria(categoria))


@when(parsers.parse("agrega {piezas:d} pieza del primer producto con stock suficiente"))
@when(parsers.parse("agrega {piezas:d} piezas del primer producto con stock suficiente"))
def agrega(cliente, piezas):
    cliente.attempts_to(AgregarProductoConStock(piezas))


@when("intenta agregar 5 piezas de un producto con stock 1")
def agrega_de_mas(cliente):
    cliente.attempts_to(AgregarMasQueElStock())


@when(parsers.parse('confirma el pedido a nombre de "{nombre}" con correo "{correo}"'))
def confirma(cliente, nombre, correo):
    cliente.attempts_to(ConfirmarPedido(nombre, correo))


@when("intenta confirmar un pedido sin productos")
def pedido_vacio(cliente):
    cliente.attempts_to(IntentarPedidoVacio())


@then(parsers.parse("ve al menos {cantidad:d} producto"))
@then(parsers.parse("ve al menos {cantidad:d} productos"))
def ve_productos(cliente, cantidad):
    assert cliente.asks_for(ProductosVisibles()) >= cantidad


@then(parsers.parse("existen al menos {cantidad:d} categorías"))
def ve_categorias(cliente, cantidad):
    assert cliente.asks_for(CategoriasDelFiltro()) >= cantidad


@then(parsers.parse('solo ve productos de "{categoria}"'))
def solo_categoria(cliente, categoria):
    assert cliente.asks_for(NombresDeCategoriaVisibles()) == {categoria}


@then(parsers.parse("el contador del carrito es {cantidad:d}"))
def contador(cliente, cantidad):
    assert cliente.asks_for(ContadorDelCarrito()) == cantidad


@then("el subtotal del carrito es mayor a 0")
def subtotal(cliente):
    assert cliente.asks_for(SubtotalDelCarrito()) > 0


@then("ve el aviso de stock insuficiente")
def aviso_stock(cliente):
    assert "insuficiente" in cliente.asks_for(AvisoVisible("stock")).lower()


@then("ve el aviso de carrito vacío")
def aviso_vacio(cliente):
    assert "vacío" in cliente.asks_for(AvisoVisible("vacio")).lower()


@then("recibe un folio de pedido")
def folio(cliente):
    assert cliente.asks_for(FolioDelPedido()).startswith("LM-")


@then("no recibe un folio de pedido")
def sin_folio(cliente):
    assert cliente.asks_for(FolioDelPedido()) == ""
