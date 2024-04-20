from django.urls import path, include
from .views import (
    JournalView,
    JournalViewDetail
)

app_name = "journal"
urlpatterns = [
    path('', JournalView.as_view()),
    path('/<int:id>', JournalViewDetail.as_view()),
]