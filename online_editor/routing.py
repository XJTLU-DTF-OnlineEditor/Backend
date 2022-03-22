from sys import path

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'V1/editor/(?P<code_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]