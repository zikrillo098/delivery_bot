from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import re
import sqlite3

database = sqlite3.connect('wallpapers.db')
cursor = database.cursor()

load_dotenv()

URL = os.getenv('URL')
HOST = os.getenv('HOST')


class Parser:
    def __init__(self, url, name, category_id, pages=3, download=False):
        self.url = url
        self.name = name
        self.category_id = category_id
        self.pages = pages
        self.download = download

    def get_html(self, i):
        try:
            html = requests.get(self.url + f'/page{i}').text
            return html
        except Exception as e:
            print('Не удалось получить данные', e)

    def get_soup(self, i):
        html = self.get_html(i)
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def get_data(self):
        if self.name not in os.listdir():
            os.mkdir(str(self.name))

        for i in range(1, self.pages + 1):  # range (1, 3) - > 1, 2
            soup = self.get_soup(i)
            images_blocks = soup.find_all('a', class_='wallpapers__link')
            for block in images_blocks:
                page_link = HOST + block['href']
                print(page_link)
                page_html = requests.get(page_link).text
                page_soup = BeautifulSoup(page_html, 'html.parser')
                section = page_soup.find_all('span', class_='wallpaper-table__cell')[1].get_text(strip=True)
                print(section)
                image_link = block.find('img', class_='wallpapers__image').get('src')
                print(image_link)
                image_link = image_link.replace('300x168', section)
                print(image_link)

                cursor.execute('''
                INSERT OR IGNORE INTO images (image_link, category_id)
                VALUES (?, ?);
                ''', (image_link, self.category_id))


def parsing():
    html = requests.get(URL).text
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find('ul', class_='filters__list')
    filters = block.find_all('a', class_='filter__link')
    for filter in filters:
        link = HOST + filter.get('href')
        name = filter.get_text(strip=True)
        true_name = re.findall(r'[3]*[a-zA-Zа-яА-Яё]+', name)[0]
        pages = int(re.findall(r'[0-9][0-9]+', name)[0]) // 15

        cursor.execute('''
        INSERT OR IGNORE INTO categories (category_name) VALUES (?);
        ''', (true_name,))
        database.commit()

        print(f'Парсим категорию {true_name}')

        cursor.execute('''
        SELECT category_id FROM categories WHERE category_name = ?;
        ''', (true_name,))

        category_id = cursor.fetchone()[0]

        parser = Parser(url=link,
                        name=true_name,
                        category_id=category_id
                        )

        parser.get_data()


parsing()
