from django.shortcuts import render


def home(request):
    """
    首頁視圖
    """
    return render(request, 'home.html')
