from django.shortcuts import render

# Create your views here.from django.shortcuts import render
from django.shortcuts import HttpResponse


# Create your views here.
def home(request):
    # html = '<html><body>Home</body></body>'
    # return HttpResponse(html)
    return render(request, 'home.html',{'active_menu': 'home'})#返回html页面
