from screenplay.abilities import BrowseTheWeb


class ProductosVisibles:
    def answered_by(self, actor) -> int:
        return actor.ability_to(BrowseTheWeb).page.locator("[data-testid='product-card']").count()


class CategoriasDelFiltro:
    def answered_by(self, actor) -> int:
        pagina = actor.ability_to(BrowseTheWeb).page
        return pagina.locator("[data-testid='category-filter']:not([data-category='todas'])").count()


class NombresDeCategoriaVisibles:
    def answered_by(self, actor) -> set[str]:
        pagina = actor.ability_to(BrowseTheWeb).page
        textos = pagina.locator("[data-testid='product-card'] [data-testid='product-category']").all_text_contents()
        return set(textos)


class ContadorDelCarrito:
    def answered_by(self, actor) -> int:
        texto = actor.ability_to(BrowseTheWeb).page.locator("[data-testid='cart-count']").inner_text()
        return int(texto.strip())


class SubtotalDelCarrito:
    def answered_by(self, actor) -> int:
        valor = actor.ability_to(BrowseTheWeb).page.locator("[data-testid='cart-total']").get_attribute("data-total")
        return int(valor or "0")


class AvisoVisible:
    def __init__(self, tipo: str):
        self.tipo = tipo

    def answered_by(self, actor) -> str:
        aviso = actor.ability_to(BrowseTheWeb).page.locator(f"[data-testid='aviso'][data-tipo='{self.tipo}']")
        if not aviso.is_visible():
            return ""
        return aviso.inner_text()


class FolioDelPedido:
    def answered_by(self, actor) -> str:
        folio = actor.ability_to(BrowseTheWeb).page.locator("[data-testid='order-folio']")
        if not folio.is_visible():
            return ""
        return folio.get_attribute("data-folio") or ""
