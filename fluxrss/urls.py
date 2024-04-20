from django.urls import path, include
from .views import (
    FluxRssView,
    FluxRssViewDetail
)

app_name = "fluxrss"
urlpatterns = [
    path('', FluxRssView.as_view()),
    path('/<int:id>', FluxRssViewDetail.as_view()),
]