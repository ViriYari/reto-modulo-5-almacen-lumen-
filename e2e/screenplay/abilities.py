class BrowseTheWeb:
    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    @classmethod
    def using(cls, page, base_url: str) -> "BrowseTheWeb":
        return cls(page, base_url)
