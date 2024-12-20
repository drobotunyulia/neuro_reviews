import requests
from bs4 import BeautifulSoup
import json
import html
import re
import psycopg2

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
