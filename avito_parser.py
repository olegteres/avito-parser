"""
Задача:  

1. Написать скрипт на Python для парсинга объявлений о недвижимости в Южном федеральном округе России с www.avito.ru.   

2. Данные должны сохраняться в XML-файлы, разбитые по 2000 объявлений в каждом.  

3. Поля для парсинга:  
   - Заголовок объявления  
   - Цена  
   - Адрес  
   - Площадь (м²)  
   - Ссылка на объявление  
   - Дата публикации  

4. Обеспечить обработку ошибок (например, недоступность страницы).  

Важно:
- Использование библиотек (BeautifulSoup, Scrapy, requests и т.д.).  
- Оптимизация работы с большими объемами данных.  
- Чистота кода и документации.  





Решение:

Буду использовать:
- requests - для загрузки страниц.
- BeautifulSoup - для парсинга HTML-кода страниц.
- lxml - для быстрой и эффективной работы с HTML/XML.
- xml.etree.ElementTree - для генерации XML-файлов.
- time + random - для задержек между запросами, чтобы не банили.

Методы оптимизации:
- Делать паузы между запросами.
- Обрабатывать ошибки сети.
- Соблюдать лимит в 2000 объявлений на XML-файл.
- Собирать только нужные данные.

Структура скрипта:
- Собирать ссылки на объявления.
- Заходить в каждое объявление и забирать нужные данные.
- Хранить объявления в списке.
- Когда наберётся 2000 — сохранить в XML.
- Повторять до тех пор, пока парсишь.

"""


import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import os
import random

# Список User-Agent для смены
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def get_page(url, retries=3):
    """Функция для получения HTML страницы с обработкой ошибок"""
    headers = {"User-Agent": random.choice(USER_AGENTS)}  # Случайный User-Agent
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print("Слишком много запросов! Ждем 30 секунд...")
                time.sleep(30)  # Если Avito блокирует, ждем
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
        time.sleep(random.randint(10, 20))  # Увеличенные задержки
    return None

def parse_list_page(html):
    """Функция для извлечения ссылок на объявления с одной страницы списка"""
    soup = BeautifulSoup(html, 'lxml')
    ads = soup.find_all('div', class_='iva-item-root-_lk9K')
    links = [f"https://www.avito.ru{ad.find('a')['href']}" for ad in ads if ad.find('a')]
    return links

def parse_ad_page(html):
    """Функция для извлечения данных из объявления"""
    soup = BeautifulSoup(html, 'lxml')
    try:
        title = soup.find('h1', class_='title-info-title-text').text.strip()
        price = soup.find('span', class_='js-item-price').text.strip()
        address = soup.find('span', class_='item-address__string').text.strip()
        area = soup.find('li', class_='params-paramsList__item')
        area = area.text.strip() if area else 'Не указано'
        date = soup.find('div', class_='title-info-metadata-item-redesign').text.strip()
        return {
            'title': title,
            'price': price,
            'address': address,
            'area': area,
            'date': date
        }
    except AttributeError:
        return None

def save_to_xml(data, filename):
    """Функция для сохранения данных в XML-файл"""
    root = ET.Element('ads')
    for ad in data:
        ad_elem = ET.SubElement(root, 'ad')
        for key, value in ad.items():
            ET.SubElement(ad_elem, key).text = value
    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)

def main():
    BASE_URL = "https://www.avito.ru/rostov-na-donu/kvartiry/prodam"
    ads_data = []
    page = 1
    ad_count = 0
    file_index = 1

    while ad_count < 6000:  # Ограничение на 6000 объявлений (3 файла по 2000)
        print(f"Парсим страницу {page}")
        page_url = f"{BASE_URL}?p={page}"
        html = get_page(page_url)
        if not html:
            break

        ad_links = parse_list_page(html)
        for link in ad_links:
            ad_html = get_page(link)
            if ad_html:
                ad_data = parse_ad_page(ad_html)
                if ad_data:
                    ad_data['url'] = link  # Добавляем ссылку
                    ads_data.append(ad_data)
                    ad_count += 1

                    if ad_count % 2000 == 0:  # Сохранение в файл каждые 2000 объявлений
                        save_to_xml(ads_data, f"ads_{file_index}.xml")
                        print(f"Файл ads_{file_index}.xml сохранен")
                        ads_data = []
                        file_index += 1
        
        page += 1
        time.sleep(random.randint(10, 20))  # Увеличенные задержки между запросами страниц
    
    if ads_data:  # Сохранение оставшихся объявлений
        save_to_xml(ads_data, f"ads_{file_index}.xml")
        print(f"Файл ads_{file_index}.xml сохранен")

if __name__ == "__main__":
    main()
