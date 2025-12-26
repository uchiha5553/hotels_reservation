from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import OdaTipi, Oda, Musteri, Rezervasyon, Odeme, Hizmet

@admin.register(OdaTipi)
class OdaTipiAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'fiyat', 'kapasite', 'kalan_oda_sayisi')

@admin.register(Hizmet)
class HizmetAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'ikon', 'ucretli_mi')

@admin.register(Oda)
class OdaAdmin(admin.ModelAdmin):
    list_display = ('oda_no', 'oda_tipi', 'musait_mi')

admin.site.register(Musteri)
admin.site.register(Rezervasyon)
admin.site.register(Odeme)