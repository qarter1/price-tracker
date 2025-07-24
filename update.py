import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extract_price(text):
    numbers = re.findall(r"[\d ]+", text)
    number = "".join(numbers).replace(" ", "")
    return int(number) if number else None

def fetch_price(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    prices = soup.select(".product-page-price")
    prices = [p.get_text(strip=True) for p in prices]

    discount_price = None
    original_price = None

    if len(prices) == 2:
        if "-" in prices[0]:
            discount_price = extract_price(prices[0])
            original_price = extract_price(prices[1])
        else:
            original_price = extract_price(prices[0])
            discount_price = extract_price(prices[1])
    elif len(prices) == 1:
        discount_price = original_price = extract_price(prices[0])

    return discount_price, original_price

def main():
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    results = []
    for product in products:
        try:
            discount, original = fetch_price(product["url"])
        except Exception as e:
            discount = original = None
        results.append({
            "name": product["name"],
            "url": product["url"],
            "discount_price": discount,
            "original_price": original
        })

    output = {
        "date": datetime.utcnow().isoformat() + "Z",
        "products": results
    }

    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
