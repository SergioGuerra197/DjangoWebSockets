from django.urls import path 
from . import consumers

websocket_urlpatterns = [
    path('ws/bingo/', consumers.BingoConsumer.as_asgi()),
]