from django.shortcuts import render


def home(request):
    return render(request,'frontend/anaSayfa.html')

def hakkinda(request):
    return render(request,"frontend/hakkinda.html")

def odalar(request):
    return render(request,"frontend/odalar.html")
