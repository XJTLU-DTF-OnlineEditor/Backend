from django.shortcuts import render

# Create your views here.from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.cache import cache_page
@cache_page(60*5) #设置15min 前端修改会在5min之后同步


# Create your views here.
def home(request):
    # html = '<html><body>Home</body></body>'
    # return HttpResponse(html)
    return render(request, 'home.html',{'active_menu': 'home'})#返回html页面
