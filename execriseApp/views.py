from django.shortcuts import render
from django.shortcuts import HttpResponse

def basic(request):
    html = '<html><body>基础教程</body></html>'
    return HttpResponse(html)
def higher(request):
    html = '<html><body>进阶教程</body></html>'
    return HttpResponse(html)
def data(request):
    html = '<html><body>数据分析</body></html>'
    return HttpResponse(html)
