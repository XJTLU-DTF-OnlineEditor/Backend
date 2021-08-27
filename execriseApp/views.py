from django.shortcuts import render
from django.shortcuts import HttpResponse

def basic(request):
    html = '<html><body>Python3 教程</body></html>'
    return HttpResponse(html)
def higher(request):
    html = '<html><body>进阶教程</body></html>'
    return HttpResponse(html)
def data(request):
    html = '<html><body>Python3 待定</body></html>'
    return HttpResponse(html)
