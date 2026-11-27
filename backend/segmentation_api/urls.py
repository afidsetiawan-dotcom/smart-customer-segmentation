
from django.urls import path
from . import views

urlpatterns = [
    path(
        "segments/",
        views.customer_segments,
        name="customer-segments"
    ),
]
