# from _typeshed import FileDescriptor
# from typing import NewType
from django.http.response import JsonResponse
from pyquery import PyQuery as pq
from django.shortcuts import get_object_or_404, render
from . models import MyCourse
from django.core.paginator import Paginator

def Courses(request, courseName):
    error_code = 200
    msg = "success"
    submenu = courseName
    if courseName == 'basic':
        courseName = '基础教程'
    elif courseName == 'heigher':
        courseName = '高阶教程'
    else:
        courseName = '数据分析'
    courseList = MyCourse.objects.all().filter(courseType = courseName).order_by('-updateDate')
    for mycourses in courseList:
        html = pq(mycourses.description)  # 使用pq方法解析html内容
        mycourses.mytxt = pq(html)('p').text()  # 截取html段落文字
    #分页函数
    p = Paginator(courseList, 5)
    if p.num_pages <= 1:
        pageData = ''
    else:
        page = int(request.GET.get('page',1))
        courseList = p.page(page)
        left = []
        right = []
        left_has_more = False
        right_has_more = False
        first = False
        last = False
        total_pages = p.num_pages
        page_range = p.page_range
        if page == 1:
            right = page_range[page:page + 2]
            print(total_pages)
            if right[-1] < total_pages - 1:
                right_has_more
            if right[-1] < total_pages:
                last = True
        elif page == total_pages:
            left = page_range[(page-3) if (page - 3) > 0 else 0 : page - 1 ]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        else:
            left = page_range[(page-3) if (page - 3) > 0 else 0 : page - 1 ]
            right = page_range[page : page + 2]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True        
        pageData = {
            'left' : left,
            'right' : right,
            'left_has_more' : left_has_more,
            'right_has_more' : right_has_more,
            'first' : first,
            'last' : last,
            'total_pages' : total_pages,
            'page' : page,
        }
    return render(
        request, 'courseList.html', {
            'active_menu' : 'Courses',
            'sub_menu' : submenu,
            'courseName' : courseName,
            'courseList' :courseList,
            'pageData':pageData,
        })
    #     data = {
    #          'active_menu' : 'Courses',
    #         'sub_menu' : submenu,
    #         'courseName' : courseName,
    #         'courseList' :courseList,
    #         'pageData':pageData,
    #     }
    # return JsonResponse(data)
def coursesDetail(request, id):
    mycourses = get_object_or_404(MyCourse, id = id)
    mycourses.views += 1
    mycourses.save()
    return render(request, 'courseDetail.html', {
            'active_menu': 'Courses',
            'mycourses': mycourses, 
    })
    # return JsonResponse({
    #                      'active_menu': 'course',
    #                      'mycourses' : mycourses,
    # })

def search(request):
    keyword = request.GET.get('keyword')
    courseList = MyCourse.objects.filter(title__icontains=keyword)
    courseName = "关于 " + "\"" + keyword + "\"" + " 的搜索结果"
    return render(request, 'searchList.html', {
        'active_menu': 'Courses',
        'newName': courseName,
        'newList': courseList,
    })
