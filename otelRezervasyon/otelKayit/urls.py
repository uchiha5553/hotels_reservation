from django.urls import path

from otelKayit import views

urlpatterns = [
    path('',views.home,name='anaSayfa'),
    path('home/',views.home,name='anaSayfa'),
    path('hakkinda/',views.hakkinda,name='hakkinda'),
    path('odalar/',views.odalar,name='odalar')
]