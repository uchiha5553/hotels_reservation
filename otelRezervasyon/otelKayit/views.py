from django.utils import timezone
import random
from django.shortcuts import render, get_object_or_404, redirect
from .models import Oda, Odeme, Rezervasyon, Musteri, OdaTipi

def home(request):
    odalari_guncelle()
    return render(request,'frontend/anaSayfa.html')

def hakkinda(request):
    return render(request,"frontend/hakkinda.html")

def odalar(request):
    oda_tipleri = OdaTipi.objects.all()
    return render(request, 'frontend/odalar.html', {'oda_tipleri': oda_tipleri})

def oda_detay(request, id):
    oda_tipi = get_object_or_404(OdaTipi, id=id)
    return render(request, 'frontend/oda_detay.html', {'oda_tipi': oda_tipi})

def odalari_guncelle():
    bugun = timezone.now().date()
    # Çıkış tarihi bugün veya daha eski olan, hala dolu gözüken odaları bul
    biten_rezervasyonlar = Rezervasyon.objects.filter(cikis_tarihi__lt=bugun)
    for rez in biten_rezervasyonlar:
        oda = rez.oda
        if not oda.musait_mi:
            oda.musait_mi = True
            oda.save()
            # Kalan oda sayısını artır
            tip = oda.oda_tipi
            tip.kalan_oda_sayisi += 1
            tip.save()

def rezervasyon_yap(request, oda_tipi_id):
    odalari_guncelle() 
    oda_tipi = get_object_or_404(OdaTipi, id=oda_tipi_id)
    
    if request.method == 'POST':
        # 1. Ana Misafir Bilgileri
        ad = request.POST.get('ad')
        soyad = request.POST.get('soyad')
        tc = request.POST.get('tc_no')
        tel = request.POST.get('telefon')
        email = request.POST.get('email')
        kisi_sayisi = int(request.POST.get('kisi_sayisi', 1))
        
        # 2. Ödeme Yöntemi (Burayı ekledik kanka!)
        odeme_yontemi = request.POST.get('odeme_yontemi')
        
        # 3. Ek Misafir Listeleri
        ek_adlar = request.POST.getlist('ek_ad[]')
        ek_soyadlar = request.POST.getlist('ek_soyad[]')
        ek_tcler = request.POST.getlist('ek_tc[]')
        ek_emailler = request.POST.getlist('ek_email[]')
        ek_tellar = request.POST.getlist('ek_tel[]')

        # 4. TC Kontrolü
        if len(tc) != 11 or not tc.isdigit():
             return render(request, 'frontend/hata.html', {'mesaj': 'Ana misafir TC no 11 haneli rakam olmalıdır.'})

        # 5. Boş Oda Sorgusu
        musait_odalar = Oda.objects.filter(oda_tipi=oda_tipi, musait_mi=True)

        if musait_odalar.exists():
            secilen_oda = random.choice(musait_odalar)
            
            # 6. Ana Müşteriyi Kaydet
            ana_musteri, _ = Musteri.objects.get_or_create(
                tc_no=tc,
                defaults={'ad': ad, 'soyad': soyad, 'telefon': tel, 'email': email}
            )

            # 7. Rezervasyonu Oluştur
            yeni_rezervasyon = Rezervasyon.objects.create(
                rezervasyonu_yapan=ana_musteri,
                oda=secilen_oda,
                giris_tarihi=request.POST.get('giris_tarihi'),
                cikis_tarihi=request.POST.get('cikis_tarihi'),
                toplam_ucret=oda_tipi.fiyat,
                kişi_Sayisi=kisi_sayisi
            )

            # 8. Ödemeyi Oluştur
            Odeme.objects.create(
                rezervasyon=yeni_rezervasyon,
                tutar=yeni_rezervasyon.toplam_ucret,
                odeme_yontemi=odeme_yontemi,
                odendi_mi=(odeme_yontemi == 'kart')
            )

            # 9. Konaklayanlar Listesini Doldur
            yeni_rezervasyon.konaklayanlar.add(ana_musteri)

            for i in range(len(ek_adlar)):
                misafir, _ = Musteri.objects.get_or_create(
                    tc_no=ek_tcler[i],
                    defaults={
                        'ad': ek_adlar[i], 
                        'soyad': ek_soyadlar[i],
                        'email': ek_emailler[i] if i < len(ek_emailler) else '',
                        'telefon': ek_tellar[i] if i < len(ek_tellar) else ''
                    }
                )
                yeni_rezervasyon.konaklayanlar.add(misafir)

            # 10. Oda Durumunu Kapat ve Sayacı Düşür
            secilen_oda.musait_mi = False
            secilen_oda.save()
            
            oda_tipi.kalan_oda_sayisi -= 1
            oda_tipi.save()

            return render(request, 'frontend/basari.html', {'oda_no': secilen_oda.oda_no})
        
        return render(request, 'frontend/hata.html', {'mesaj': 'Seçtiğiniz oda tipinde boş oda kalmadı!'})

    return render(request, 'frontend/rezervasyon_formu.html', {'oda_tipi': oda_tipi})