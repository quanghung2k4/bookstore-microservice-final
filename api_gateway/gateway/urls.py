from django.urls import re_path

from gateway.views import ProxyView

urlpatterns = [
    re_path(r"^(?P<service>products|carts|orders|users|payments|shipping|ai)/(?P<path>.*)$", ProxyView.as_view()),
]
