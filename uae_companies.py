import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


def fetch_html_content(url: str, headers: dict) -> BeautifulSoup | None:
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'lxml')

            return soup
        else:
            print(f"Ошибка: {response.status_code}")

            return None

    except Exception:
        print("Ошибка: Неправильно указан URL")

        return None


def get_company_data(url: str, headers: dict) -> int:
    soup = fetch_html_content(url, headers)
    number_pages = soup.find('span', class_='pages').text.split()[-1]
    return number_pages


def main():
    base_url = 'https://www.uaecontact.com/page/1?s=interior+Design'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    result = get_company_data(base_url, headers)
    print(result)


if __name__ == '__main__':
    main()
