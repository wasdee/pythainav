from requests_html import HTMLSession

def get_nav(fund: str):

    url = "https://www.finnomena.com/fund/"
    url = url + fund
    session = HTMLSession()
    r = session.get(url)
    r.html.render()
    price = r.html.find('h3', first=True)
    return float(price.text)
