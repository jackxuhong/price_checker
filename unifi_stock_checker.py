from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from numpy.random import default_rng
import os
import requests
from requests_html import HTMLSession
import sqlite3
import sys
from time import sleep

load_dotenv()

_PRODUCT_FILE = os.getenv('PRODUCT_FILE')
_MIN_SLEEP = int(os.getenv('MIN_SLEEP'))
_MAX_SLEEP = int(os.getenv('MAX_SLEEP'))
_API_URL = os.getenv('TELEGRAM_API_URL')
_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
_PRODUCTS_DB = os.getenv('PRODUCTS_DB')


def send_alert(alerts):
    for alert in alerts:
        url = _API_URL + _BOT_TOKEN + '/sendMessage?chat_id=' + \
            _CHAT_ID + '&parse_mode=Markdown&text=' + alert
        r = requests.get(url)
        if r.status_code == 200:
            print(
                f'{datetime.now()} - Successfully sent a Telegram alert [{alert}]')
        else:
            print(
                f'{datetime.now()} - Failed to send Telegram alert [{alert}], err = {r.status_code}')
    pass


def send_daily_summary(date):
    con = sqlite3.connect(_PRODUCTS_DB)
    cur = con.cursor()

    summary = f'Daily Summary for {date}\n'
    summary += '============================\n'
    cur.execute(
        f"SELECT log_date, product_name, in_stock, MIN(price) min_price, MAX(price) max_price, COUNT(1) count FROM product_logs WHERE log_date = '{date}' group by log_date, product_name, in_stock")
    for row in cur.fetchall():
        log_date = row[0]
        product_name = row[1]
        in_stock = row[2]
        min_price = row[3]
        max_price = row[4]
        count = row[5]
        summary += f'*Product:* {product_name} *In Stock:* {in_stock} *Min Px:* {min_price} *Max Px:* {max_price} *Count:* {count}\n\n'

    con.close()

    url = _API_URL + _BOT_TOKEN + '/sendMessage?chat_id=' + \
        _CHAT_ID + '&parse_mode=Markdown&text=' + summary
    r = requests.get(url)
    if r.status_code == 200:
        print(
            f'{datetime.now()} - Successfully sent daily summary to Telegram')
    else:
        print(
            f'{datetime.now()} - Failed to send daily summary to Telegram')


def check_stock(product_urls):
    con = sqlite3.connect(_PRODUCTS_DB)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS product_logs (log_date TEXT, product_name TEXT, price REAL, in_stock TEXT, log_timestamp TEXT)")
    con.commit()

    session = HTMLSession()

    alerts = []

    for product_url in product_urls:
        # Skip blank URL
        if len(product_url.strip()) == 0:
            break

        r = session.get(product_url)
        if r.status_code == 200:
            r.html.render(timeout=30)
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
                print(f'{datetime.now()} - {item} is IN STOCK @ {price} :)')
                alert = f'{item} ({product_url}) is IN STOCK @ {price}!'
                alerts.append(alert)
            else:
                print(
                    f"{datetime.now()} - {item} is out of stock @ {price} :(")

            cur.execute(
                f"INSERT INTO product_logs VALUES ('{datetime.now():%Y-%m-%d}', '{item}', '{price}', '{in_stock}', '{datetime.now()}')")
            con.commit()

        rng = default_rng()
        time_to_sleep = rng.uniform(_MIN_SLEEP, _MAX_SLEEP)
        print(f'{datetime.now()} - Sleeping for {time_to_sleep} seconds...')
        sleep(time_to_sleep)

    if alerts:
        send_alert(alerts)
    else:
        print(f'{datetime.now()} - Nothing is available :(')

    con.close()


def main(argv):
    if len(argv) > 1:
        send_daily_summary(argv[1])
    else:
        with open(_PRODUCT_FILE) as file:
            product_urls = file.readlines()

        check_stock(product_urls)


if __name__ == '__main__':
    main(sys.argv)
