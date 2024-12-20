import requests
from bs4 import BeautifulSoup
import json
import html
import re
import psycopg2
import message

all_reviews = parse_all_pages(max_pages=15)  # Укажите количество страниц для парсинга
    print(f"Всего отзывов собрано: {len(all_reviews)}")
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(data_time) FROM review")
    last_review_date = cursor.fetchone()[0]
    if last_review_date is None:
        for reviews in all_reviews:
            insert_query = "INSERT INTO review (text, data_time) VALUES (%s, %s)"
            review_body = reviews['reviewBody']
            review_date = reviews['datePublished']
            review_body = re.sub(r'\s+', ' ', review_body).strip()
            cursor.execute(insert_query, (review_body, review_date))
    else:
        for reviews in all_reviews:
            if reviews['datePublished'] > last_review_date:
                insert_query = "INSERT INTO review (text, data_time) VALUES (%s, %s)"
                review_body = reviews['reviewBody']
                review_date = reviews['datePublished']
                review_body = re.sub(r'\s+', ' ', review_body).strip()
                cursor.execute(insert_query, (review_body, review_date))
    # Закрытие курсора и соединения
    connection.commit()
    cursor.close()
    connection.close()

    mail = message.Mail()
    mail.send_code("yudrobotun8@gmail.com")
    mail.close_connection()
