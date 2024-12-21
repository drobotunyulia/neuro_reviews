from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_page, name='review_page'),
]
