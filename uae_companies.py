import re

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


def go_to_another_page(url: str, headers: dict) -> str | None:
    soup = fetch_html_content(url, headers)
    next_link = soup.find('a', class_='nextpostslink')
    if next_link:
        url = next_link['href']
        return url
    else:
        return None


def get_company_data(url: str, headers: dict) -> list:
    companys_data = []

    while url:
        soup = fetch_html_content(url, headers)
        companys_description = soup.find_all(class_='post-list-content')

        for company in companys_description:
            company_text = company.find('p').text
            companys_data.append(company_text)

        url = go_to_another_page(url, headers)

    return companys_data


def company_data_formatting(company_data: list) -> list:
    result_list = []

    for company in company_data:
        parts = re.split(r'\b(Company Name|'
                         r'Address|'
                         r'PO Box|'
                         r'Phone|'
                         r'Fax|'
                         r'Email|'
                         r'Website|'
                         r'Business Activity|'
                         r'Nature of Business)\b', company)

        company_dict = {}
        for i in range(1, len(parts), 2):
            key = parts[i].strip()
            value = parts[i + 1].strip(': ').replace('\n', '')
            company_dict[key] = value

        result_list.append(company_dict)

    return result_list


def write_to_json(data: list, filename: str) -> None:
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main() -> None:
    base_url = 'https://www.uaecontact.com/?s=interior+Design'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    company_data = get_company_data(base_url, headers)
    data_formatting = company_data_formatting(company_data)

    write_to_json(data_formatting, 'design_and_construction_companies.json')

    count = 1
    for i in data_formatting:
        print(f'{count}. {i}')
        count += 1


if __name__ == '__main__':
    main()
