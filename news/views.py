from django.shortcuts import render
from .models import News

# Create your views here.
def news(request):
    newss = News.objects.all().order_by('-title')
    return render(request, 'news.html', {'newss': newss})

