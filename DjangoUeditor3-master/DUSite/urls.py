#coding:utf-8
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
import settings
from django.contrib import admin
from TestApp.views import  TestUEditorModel,ajaxcmd,TestUEditor

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # path('$', 'DUSite.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    path('admin/', include(admin.site.urls)),
    path('ueditor/',include('DjangoUeditor.urls')),
    path('test/$',TestUEditorModel),
    path('test2/$',TestUEditor),
    path('ajaxcmd/$',ajaxcmd)

)

if settings.DEBUG:
    urlpatterns += patterns('',
        path('media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT }),
        path('static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
        path('(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_ROOT}),
    )