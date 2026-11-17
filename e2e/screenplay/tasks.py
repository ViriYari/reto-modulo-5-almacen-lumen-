from playwright.sync_api import expect

from screenplay.abilities import BrowseTheWeb


class AbrirLaTienda:
    def perform_as(self, actor) -> None:
        navegar = actor.ability_to(BrowseTheWeb)
        navegar.page.goto(navegar.base_url)
        expect(navegar.page.locator("[data-testid='product-card']").first).to_be_visible()


class ConsultarProductos:
    def perform_as(self, actor) -> None:
        navegar = actor.ability_to(BrowseTheWeb)
        expect(navegar.page.locator("[data-testid='catalog-status']")).to_have_attribute("data-state", "ready")


class FiltrarPorCategoria:
    def __init__(self, categoria: str):
        self.categoria = categoria

    def perform_as(self, actor) -> None:
        pagina = actor.ability_to(BrowseTheWeb).page
        pagina.get_by_role("button", name=self.categoria, exact=True).click()


class AgregarProductoConStock:
    def __init__(self, piezas: int):
        self.piezas = piezas

    def perform_as(self, actor) -> None:
        pagina = actor.ability_to(BrowseTheWeb).page
        tarjeta = pagina.locator("[data-testid='product-card']").filter(
            has=pagina.locator("[data-testid='add-to-cart']:enabled")
        ).first
        stock = int(tarjeta.get_attribute("data-stock") or "0")
        if stock < 5:
            tarjeta = pagina.locator("[data-testid='product-card']").nth(0)
            for candidato in pagina.locator("[data-testid='product-card']").all():
                if int(candidato.get_attribute("data-stock") or "0") >= 5:
                    tarjeta = candidato
                    break
        tarjeta.locator("[data-testid='qty']").fill(str(self.piezas))
        tarjeta.locator("[data-testid='add-to-cart']").click()


class AgregarMasQueElStock:
    def perform_as(self, actor) -> None:
        pagina = actor.ability_to(BrowseTheWeb).page
        tarjeta = pagina.locator("[data-product-id='esc-05']")
        expect(tarjeta).to_have_attribute("data-stock", "1")
        tarjeta.locator("[data-testid='qty']").fill("5")
        tarjeta.locator("[data-testid='add-to-cart']").click()


class ConfirmarPedido:
    def __init__(self, nombre: str, correo: str):
        self.nombre = nombre
        self.correo = correo

    def perform_as(self, actor) -> None:
        pagina = actor.ability_to(BrowseTheWeb).page
        pagina.locator("[data-testid='checkout-nombre']").fill(self.nombre)
        pagina.locator("[data-testid='checkout-correo']").fill(self.correo)
        pagina.locator("[data-testid='checkout-submit']").click()


class IntentarPedidoVacio:
    def perform_as(self, actor) -> None:
        actor.ability_to(BrowseTheWeb).page.locator("[data-testid='checkout-submit']").click()
