import requests
from lxml import html
import csv

# URL веб-сайту та параметри пошуку
url = "https://uk.bn.ua/find/"
search_params = {
    "optype": "1",  # Тип об'єкта (1 - Квартира)
    "region_id": "5",  # Місто (5 - Київ)
    "with_photo": "1",  # Тільки з фото
    "currency_id": "2"  # Валюта (2 - Долар)
}

# Спеціальні заголовки для імітації браузера справжнього користувача
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xm,*/*;q=l;q=0.9,image/avif,image/webp,image/apng0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# Надсилання HTTP-запиту до форми пошуку веб-сайту з власними заголовками
response = requests.get(url, headers=headers, params=search_params)

# Встановлення кодування відповіді на UTF-8
response.encoding = 'utf-8'

print(response)
# Перевірте, чи успішно отримано сторінку
if response.status_code == 200:
    # Розбір вмісту HTML за допомогою LXML
    tree = html.fromstring(response.content)

    # Пошук реклами на сторінці
    ads = tree.xpath('//*[@id="sidebar"]/div[2]/div[contains(@class, "listingv2-item")]')
    print(ads)

    # Відкриття файлу CSV, для зберігання даних
    with open('kursowa.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Заголовок', 'Ціна', 'Площа', 'Кількість кімнат', 'Адреса', 'Дата створення',
                      'Посилання на оголошення']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Запис заголовка CSV файлу
        writer.writeheader()

        # Перегляд знайдених оголошень і збір даних
        for ad in ads:
            # //*[@id="sidebar"]/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[1]/div
            title = ad.xpath(
                './/div[@class="listingv2-param listingv2-param-cityd listingv2-ellipsed"]')
            title = title[0].text_content().encode('latin1').decode('utf-8').strip() if title else 'Недоступно'

            price = ad.xpath('.//div[@class="listingv2-prices"]//span[@class="val"]/text()')
            price = price[0].encode('latin1').decode('utf-8').strip() if price else 'Недоступно'

            area = ad.xpath('.//div[contains(@class, "listingv2-param-areas")]/text()')
            area = area[0].encode('latin1').decode('utf-8').strip() if area else 'Недоступно'

            rooms = ad.xpath('.//div[contains(@class, "listingv2-param-rooms")]/a/text()')
            rooms = rooms[0].encode('latin1').decode('utf-8').strip() if rooms else 'Недоступно'

            address_element = ad.xpath('.//div[contains(@class, "listingv2-param-cityd")]')
            if address_element:
                address = address_element[0].text_content().encode('latin1').decode('utf-8').strip()
            else:
                address = 'Недоступно'

            # Дата створення недоступна в наданій структурі HTML
            date_created = 'Недоступно'

            link_element = ad.xpath(
                './/div[contains(@class, "listingv2-item-content")]//a[contains(@href, "/realty")]/@href')
            if link_element:
                link = 'https://uk.bn.ua' + link_element[0].strip()
            else:
                link = 'Недоступно'

            # Запис даних у CSV файл
            writer.writerow({
                'Заголовок': title,
                'Ціна': price,
                'Площа': area,
                'Кількість кімнат': rooms,
                'Адреса': address,
                'Дата створення': date_created,
                'Посилання на оголошення': link
            })

    result = "Data has been successfully collected and saved to 'kursowa.csv'"
else:
    result = f"Error in retrieving the page: {response.status_code}"