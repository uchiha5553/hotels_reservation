from django.db import models

# Create your models here.

from django.db import models

class Hizmet(models.Model):
    ikon = models.CharField(max_length=50, help_text="Örn: fa-wifi, fa-swimming-pool (FontAwesome ikon adı)")
    baslik = models.CharField(max_length=100, verbose_name="Hizmet Adı")
    ucretli_mi = models.BooleanField(default=False, verbose_name="Ücretli mi?")

    class Meta:
        verbose_name_plural = "Hizmetler"

    def __str__(self):
        return self.baslik


class OdaTipi(models.Model):
    baslik = models.CharField(max_length=50, verbose_name="Oda Türü") # Standart, Suit vb.
    fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Gecelik Fiyat")
    
    # oda kapasitesi
    kapasite = models.PositiveIntegerField(default=1, verbose_name="Oda Kapasitesi (Kişi)")

    aciklama=models.TextField(verbose_name="Oda Açıklaması", blank=True, null=True)
    
    # oda sayıları
    toplam_oda_sayisi = models.PositiveIntegerField(default=0, verbose_name="Toplam Oda Sayısı")
    kalan_oda_sayisi = models.IntegerField(default=0, verbose_name="Kalan Boş Oda")

    hizmetler = models.ManyToManyField(Hizmet, blank=True, verbose_name="Oda Özellikleri")
    
    resim = models.ImageField(upload_to='oda_tipleri/', null=True, blank=True)

    def __str__(self):
        return f"{self.baslik} (Kapasite: {self.kapasite} Kişi)"

class Oda(models.Model):
    oda_no = models.CharField(max_length=10, unique=True)
    oda_tipi = models.ForeignKey(OdaTipi, on_delete=models.CASCADE)
    musait_mi = models.BooleanField(default=True)
    ozel_resim = models.ImageField(upload_to='odalar/', null=True, blank=True)

    def __str__(self):
        return f"Oda {self.oda_no} ({self.oda_tipi.baslik})"

class Musteri(models.Model):
    ad = models.CharField(max_length=50)
    soyad = models.CharField(max_length=50)
    tc_no = models.CharField(max_length=11, unique=True)
    telefon = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.ad} {self.soyad}"

class Rezervasyon(models.Model):
    rezervasyonu_yapan = models.ForeignKey(Musteri, on_delete=models.CASCADE, related_name='yapilan_rezervasyonlar')
    oda = models.ForeignKey(Oda, on_delete=models.CASCADE)
    giris_tarihi = models.DateField()
    cikis_tarihi = models.DateField()
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    #odada kalacak kişi sayısı
    kişi_Sayisi=models.PositiveIntegerField(default=1)

    #odada kalan kişiler
    konaklayanlar = models.ManyToManyField(Musteri, related_name='konaklamalar')

    toplam_ucret = models.DecimalField(max_digits=10, decimal_places=2)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rezervasyon {self.rezervasyonu_yapan} - {self.oda.oda_no} ({self.giris_tarihi})"
    



    
class Odeme(models.Model):
    ODEME_YONTEMI = [
        ('nakit', 'Nakit'),
        ('kart', 'Kredi Kartı'),
        ('havale', 'Havale/EFT'),
    ]
    rezervasyon = models.OneToOneField(Rezervasyon, on_delete=models.CASCADE, related_name="odeme_detayi")
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    odeme_yontemi = models.CharField(max_length=20, choices=ODEME_YONTEMI, default='nakit')
    odendi_mi = models.BooleanField(default=False)
    islem_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rezervasyon.id} - {self.tutar} TL"

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Rezervasyon)
def odayi_bosa_cikar_silinince(sender, instance, **kwargs):
    oda = instance.oda
    oda.musait_mi = True
    oda.save()
    
    # Oda tipindeki kalan oda sayısını da 1 artır
    oda_tipi = oda.oda_tipi
    oda_tipi.kalan_oda_sayisi += 1
    oda_tipi.save()