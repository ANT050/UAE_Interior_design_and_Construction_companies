import asyncio
import re
import json
from typing import Optional, List
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = 'https://www.uaecontact.com/?s=interior+Design'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}


async def fetch_html_content(session: aiohttp.ClientSession, url: str) -> Optional[BeautifulSoup]:
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'lxml')
                return soup
            else:
                print(f"Ошибка: {response.status}")
                return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


async def go_to_another_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    soup = await fetch_html_content(session, url)
    next_link = soup.find('a', class_='nextpostslink')
    if next_link:
        return next_link['href']
    else:
        return None


async def get_company_data(session: aiohttp.ClientSession, url: str) -> List[str]:
    companies_data = []

    while url:
        soup = await fetch_html_content(session, url)
        companies_description = soup.find_all(class_='post-list-content')

        for company in companies_description:
            company_text = company.find('p').text

            print(company_text)

            companies_data.append(company_text)

        url = await go_to_another_page(session, url)

    return companies_data


def company_data_formatting(company_data: List[str]) -> List[dict]:
    result_list = []

    for company in company_data:
        parts = re.split(r'\b(Company Name|'
                         r'Address|'
                         r'PO Box|'
                         r'Phone|'
                         r'Tel|'
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


def write_to_json(data: List[dict], filename: str) -> None:
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def write_to_csv(data: List[dict], filename: str) -> None:
    df = pd.DataFrame(data)

    df = df.sort_values(by='Company Name')
    df['Phone'] = df['Phone'].fillna('') + df['Tel'].fillna('')
    df = df.drop(columns=['Tel'])
    df['Business Activity'] = df['Business Activity'].fillna('') + df['Nature of Business'].fillna('')
    df = df.drop(columns=['Nature of Business'])

    df.columns = [
        'Company Name',
        'Address',
        'PO Box',
        'Phone',
        'Fax',
        'Email',
        'Website',
        'Business Activity',
    ]
    df.to_csv(filename, index=False)


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        company_data = await get_company_data(session, BASE_URL)

    data_formatting = company_data_formatting(company_data)

    write_to_csv(data_formatting, 'design_and_construction_companies.csv')
    write_to_json(data_formatting, 'design_and_construction_companies.json')


if __name__ == '__main__':
    asyncio.run(main())
