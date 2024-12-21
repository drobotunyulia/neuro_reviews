from django.shortcuts import render
from django.http import HttpResponse
from .models import Review
from .models import QualityIndex
from . import message

def review_page(request):
    # Получаем данные для графика

    gratitude_count = count_gratitude_reviews()
    claim_count = count_claim_reviews()
    offer_count = count_offer_reviews()


    # Получаем последние 5 индексов качества
    last_five_quality_indexes = get_last_five_quality_indexes()

    # Формируем списки для графика: даты и индексы качества
    quality_dates = [index['data'].strftime('%Y-%m-%d') for index in last_five_quality_indexes]
    quality_values = [index['quality_index'] for index in last_five_quality_indexes]


    # Передаем данные в контекст
    context = {
        'total_reviews': Review.objects.count(),
        'last_review_date': Review.objects.latest('data_time').data_time,
        'gratitude_count': gratitude_count,
        'claim_count': claim_count,
        'offer_count': offer_count,
        'quality_dates': quality_dates,
        'quality_values': quality_values,
    }

    mail = message.Mail()
    mail.send_code("yudrobotun8@gmail.com", quality_values[0])
    return render(request, 'review/review.html', context)

def count_gratitude_reviews():
    return Review.objects.filter(class_field='благодарность').count()

def count_claim_reviews():
    return Review.objects.filter(class_field='претензия').count()

def count_offer_reviews():
    return Review.objects.filter(class_field='предложение').count()


def get_last_five_quality_indexes():
    # Получаем последние 5 записей, отсортированных по дате
    last_five_indexes = QualityIndex.objects.all().order_by('-data')[:5]

    # Формируем список с результатами
    result = []
    for index in last_five_indexes:
        result.append({
            'quality_index': float(index.quality_index),  # Преобразуем Decimal в float
            'data': index.data
        })

    return result
