from django.conf.urls import url, include

from . import views

# ocr_processor/
urlpatterns = [
    # url(r'^proxy/$', views.ocr_proxy, name='ocr-proxy'),
    url(r'^proxy/$', views.receiptCreateView.as_view(), name='test'),
    # url(r'person/$',views.PersonListCreateView.as_view(),name='person-list-create'),
    url(r'^processed/$', views.processedReceiptCreateView.as_view(), name='processed-create'),
]