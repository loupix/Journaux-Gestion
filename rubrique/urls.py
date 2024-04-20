from django.urls import path, include
from .views import (
    RubriqueView,
    RubriqueViewDetail
)

app_name = "rubrique"
urlpatterns = [
    path('', RubriqueView.as_view()),
    path('/<int:id>', RubriqueViewDetail.as_view()),
]