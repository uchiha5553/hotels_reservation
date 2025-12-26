from django.urls import path

from otelKayit import views

urlpatterns = [
    path('',views.home,name='anaSayfa'),
    path('home/',views.home,name='anaSayfa'),
    path('hakkinda/',views.hakkinda,name='hakkinda'),
    path('odalar/',views.odalar,name='odalar'),
    path('oda/<int:id>/', views.oda_detay, name='oda_detay'),
    path('odalar/rezervasyon/<int:oda_tipi_id>/', views.rezervasyon_yap, name='rezervasyon_yap'),
]