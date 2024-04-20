# item/urls.py

from django.urls import path, include
from .views import (
    ItemView,
    ItemViewDetail
)

app_name = "item"
urlpatterns = [
    path('', ItemView.as_view()),
    path('/<int:id>', ItemViewDetail.as_view()),
]