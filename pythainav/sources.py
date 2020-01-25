from abc import ABC
from abc import abstractmethod



class Source(ABC):
    @abstractmethod
    def get(self, fund: str):
        pass

    @abstractmethod
    def list(self):
        pass


class Finnomena(Source):
    def __init__(self):
        super().__init__()

    def get(self, fund: str):
        from requests_html import HTMLSession

        baseurl = "https://www.finnomena.com/fund/"
        # TODO: parse ilegal fund name "BP33/19" -> "BP33%2F19"
        url = baseurl + fund
        session = HTMLSession()
        r = session.get(url)
        r.html.render()
        price = r.html.find("h3", first=True)
        return float(price.text)

    def list(self):
        # TODO
        pass


class Sec(Source):
    def __init__(self, subscription_key):
        # TODO: WIP
        super().__init__()

    def get(fund: str):
        # TODO: WIP
        pass

    def list(self):
        # TODO: WIP
        pass
