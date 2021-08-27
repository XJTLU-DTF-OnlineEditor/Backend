from django.shortcuts import render
from django.shortcuts import HttpResponse

def hot(request):
    html = '<html><body>热门评论</body></html>'
    return HttpResponse(html)
def new(request):
    html = '<html><body>最新评论</body></html>'
    return HttpResponse(html)
