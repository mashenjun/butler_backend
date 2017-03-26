from django.conf.urls import url, include

from . import views

# ocr_processor/
urlpatterns = [
    url(r'^proxy/$', views.ocr_proxy, name='ocr-proxy'),
    url(r'^test/$', views.receiptCreateView.as_view(), name='test'),
]