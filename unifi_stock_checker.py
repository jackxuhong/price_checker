from bs4 import BeautifulSoup
from numpy.random import default_rng
from requests_html import HTMLSession
from time import sleep


def stock_checker(product_urls):
    session = HTMLSession()

    for product_url in product_urls:
        r = session.get(product_url)
        if r.status_code == 200:
            r.html.render()
            item = 'No name'
            price = 0
            in_stock = False

            item_div = r.html.find('.sc-y8tnx3-6', first=True)
            if item_div:
                item = item_div.text

            price_div = r.html.find('.sc-1pbdt8j-9', first=True)
            if price_div:
                price = price_div.text

            divs = r.html.find('.sc-plhx78-2')
            for div in divs:
                if 'Add to Cart' in div.text:
                    in_stock = True
                    break

            if in_stock:
                print(f'{item} in stock @ {price}')
            else:
                print(f"{item} is out of stock @ {price}")

        rng = default_rng()
        time_to_sleep = rng.uniform(1, 5)
        print(f'Sleeping for {time_to_sleep} seconds...')
        sleep(time_to_sleep)


product_urls = [
    'https://ca.store.ui.com/ca/en/products/dream-router',
    'https://ca.store.ui.com/ca/en/products/unifi-ap-6-lite',
    'https://ca.store.ui.com/ca/en/products/unifi-switch-lite-8-poe',
    'https://ca.store.ui.com/ca/en/collections/bestseller/products/dream-machine-se']
stock_checker(product_urls)
