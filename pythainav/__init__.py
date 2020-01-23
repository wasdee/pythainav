from requests_html import HTMLSession

def get_nav(fund: str):

    url = "https://www.finnomena.com/fund/"
    # TODO: parse ilegal fund name "BP33/19" -> "BP33%2F19"
    url = url + fund
    session = HTMLSession()
    r = session.get(url)
    r.html.render()
    price = r.html.find('h3', first=True)
    return float(price.text)
