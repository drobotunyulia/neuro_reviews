import requests
from bs4 import BeautifulSoup
import json
import html
import re
import psycopg2
import schedule
import classification

dbname = 'reviews'
user = 'postgres'
password = ''
host = 'localhost'
port = '5432'

connection = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
# Устанавливаем URL и headers
base_url = "https://www.banki.ru/services/responses/bank/promsvyazbank/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def parse_page(page_number):
    params = {
        "page": page_number,
        "is_countable": "on",
    }
    response = requests.get(base_url, headers=headers, params=params)
    html_content = response.text
    with open("example.txt", "w") as file:
        file.write(html_content)
    soup = BeautifulSoup(html_content, "lxml")
    reviews = soup.find("script", type="application/ld+json")
    reviews = reviews.text
    cleaned_content = re.sub(r'[\x00-\x1F\x7F]', '', reviews)
    data = json.loads(cleaned_content)
    all_reviews = []
    if data.get("@type") == "Organization" and "review" in data:
        for review in data["review"]:
            review_body = review.get("description", "N/A")
            date_published = review.get("datePublished", "N/A")
            all_reviews.append({"reviewBody": review_body, "datePublished": date_published})
    cleaned_reviews = []
    for review_data in all_reviews:
        decoded_date = html.unescape(review_data['datePublished'])
        cleaned_date = re.sub(r'<[^>]+>', '', decoded_date)
        print(f"Date: {cleaned_date}")
        decoded_data = html.unescape(review_data['reviewBody'])
        cleaned_data = re.sub(r'<[^>]+>', '', decoded_data)
        cleaned_review = re.sub(r'</?p>', '', cleaned_data)
        print(f"Review: {cleaned_review}")
        print("---")
        cleaned_reviews.append({"reviewBody": cleaned_review, "datePublished": cleaned_date})
    return cleaned_reviews



def parse_all_pages(max_pages=100):
    all_reviews = []
    for page_number in range(1, max_pages + 1):
        reviews = parse_page(page_number)
        all_reviews.extend(reviews)
    return all_reviews

def run_parser():
    """
    Основная функция для запуска парсинга.
    """
    print(f"Запуск парсинга: {datetime.now()}")

    all_reviews = parse_all_pages(max_pages=15)
    print(f"Всего отзывов собрано: {len(all_reviews)}")
    cursor = connection.cursor()

    cursor.execute("SELECT MAX(data_time) FROM review")
    last_review_date = cursor.fetchone()[0]

    if last_review_date is None:
        all_reviews_for_class = []
        for reviews in all_reviews:
            insert_query = "INSERT INTO review (text, data_time) VALUES (%s, %s)"
            review_body = reviews['reviewBody']
            review_date = reviews['datePublished']
            review_body = re.sub(r'\s+', ' ', review_body).strip()
            cursor.execute(insert_query, (review_body, review_date))
            connection.commit()
            all_reviews_for_class.append(review_body)
        all_classes = classification.eval_net(
            all_reviews_for_class,
            classification.imported_model,
            classification.imported_tokenizer,
            classification.imporeted_label_encoder
        )
    else:
        all_new_reviews_for_class = []
        for reviews in all_reviews:
            dt = datetime.strptime(reviews['datePublished'], "%Y-%m-%d %H:%M:%S")
            tz = pytz.timezone('Etc/GMT-3')
            dt_with_tz = tz.localize(dt)
            if dt_with_tz > last_review_date:
                insert_query = "INSERT INTO review (text, data_time) VALUES (%s, %s)"
                review_body = reviews['reviewBody']
                review_date = reviews['datePublished']
                review_body = re.sub(r'\s+', ' ', review_body).strip()
                cursor.execute(insert_query, (review_body, review_date))
                connection.commit()
                all_new_reviews_for_class.append(review_body)
        all_classes = classification.eval_net(
            all_new_reviews_for_class,
            classification.imported_model,
            classification.imported_tokenizer,
            classification.imporeted_label_encoder
        )

    cursor.execute("SELECT id_review FROM review ORDER BY id_review")
    existing_ids = [row[0] for row in cursor.fetchall()]

    if len(all_classes) != len(existing_ids):
        raise ValueError("Количество классов не соответствует количеству записей в таблице review!")

    for class_review, id_review in zip(all_classes, existing_ids):
        update_query = "UPDATE review SET class = %s WHERE id_review = %s"
        cursor.execute(update_query, (class_review, id_review))
        connection.commit()

    query = "SELECT COUNT(*) FROM review WHERE class = %s;"
    params = ('благодарность',)
    cursor.execute(query, params)
    count_gratitude = cursor.fetchone()[0]

    params = ('претензия',)
    cursor.execute(query, params)
    count_claim = cursor.fetchone()[0]

    params = ('предложение',)
    cursor.execute(query, params)
    count_offer = cursor.fetchone()[0]

    quality_index_value = quality_index(count_gratitude, count_claim, count_offer)

    insert_query = "INSERT INTO quality_index (quality_index, data) VALUES (%s, %s)"
    current_date = datetime.now()
    date_string = current_date.strftime("%Y-%m-%d")
    cursor.execute(insert_query, (quality_index_value, date_string))

    connection.commit()
    cursor.close()
    print("Парсинг завершен.")


# Настройка расписания
schedule.every(1).hours.do(run_parser)  # Запускать каждый час

print("Программа запущена. Ожидание запуска задач...")
while True:
    schedule.run_pending()
    time.sleep(1)

