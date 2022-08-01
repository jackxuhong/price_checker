from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from numpy.random import default_rng
import os
import requests
from requests_html import HTMLSession
from time import sleep

session = HTMLSession()
product_url = 'https://www.amazon.ca/dp/B08HMLKS2N'
#product_url = 'https://www.amazon.ca/dp/B007A9TD3E'
r = session.get(product_url)
r.html.render(timeout=30)
price_parent = r.html.find('span.a-price', first=True)
price = price_parent.find('span.a-offscreen', first=True).text
print(price)
