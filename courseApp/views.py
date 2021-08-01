# from _typeshed import FileDescriptor
# from typing import NewType
from django.http.response import JsonResponse
from pyquery import PyQuery as pq
from django.shortcuts import get_object_or_404, render
from . models import MyCourse,Topic
from django.core.paginator import Paginator
import json
from datetime import date, datetime
from django.core import serializers #JsonResponse用来将QuerySet序列化

"""
如果用JsonResponse处理上传日期需要对相应update_data进行处理
"""
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

"""
如果用JsonResponse处理MyCourse需要对整体进行处理
"""
class MyCourseEncoder(json.JSONEncoder ):
    def default(self, obj):
        if isinstance(obj, MyCourse):
            return obj.__str__()
        return json.JSONEncoder.default(self, obj)

"""

render 形式返回课程页面

"""
def Courses1(request, topic_title):
    if request.method == 'GET':
        submenu = topic_title
        if topic_title == 'basic':
            topic_title = '基础课程'
        elif topic_title == 'heigher':
            topic_title = '高阶课程'
        else:
            topic_title = '数据分析'
        courseList = MyCourse.objects.all().filter(topic_name = topic_title).order_by('-update_date')
        for mycourses in courseList:
            html = pq(mycourses.description)  # 使用pq方法解析html内容
            mycourses.mytxt = pq(html)('p').text()  # 截取html段落文字
    # 分页函数
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
                    right_has_more = True
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
                "error_code": 200,
                "msg": 'success',
                'active_menu' : 'Courses',
                'sub_menu' : submenu,
                'topic_title' : topic_title,
                'courseList' :courseList,
                'pageData':pageData,
            })
    else:
       return render(
            request, 'courseList.html', {
                "error_code": 400,
                "msg": 'INVALID REQUEST',
                'active_menu' : 'Courses',
                
            })
  
   


def Courses(request, topic_title):
    if request.method == 'GET':
        submenu = topic_title
        if topic_title == 'basic':
            topic_title = '基础课程'
        elif topic_title == 'heigher':
            topic_title = '高阶课程'
        else:
            topic_title = '数据分析'
        courseList = serializers.serialize("json",MyCourse.objects.all()
                                            .filter(topic_name = topic_title)
                                            .order_by('-update_date'))
        result = {
            "error_code": 200,
            "msg": 'success',
            'active_menu' : 'Courses',
            'sub_menu' : submenu,
            'topic_title' : topic_title,
            # 'topic_content':Topic.objects.get(topic_title=topic_title).topic_content, #还没建
            'courseList' :json.loads(courseList),


        }
        return JsonResponse(result, safe=False)
    else:
        result={
            "error_code": 400,
            'msg':'INVALID REQUEST'
        }
        return JsonResponse(result)
"""
render形式的返回
节省对应到html抛去不必要变量
节省工作量
"""
# def coursesDetail(request, subtopic_id):
#     if request.method == 'GET':
#         mycourses = get_object_or_404(MyCourse, subtopic_id = subtopic_id)
#         mycourses.views += 1
#         mycourses.save()
#         return render(request, 'courseDetail.html', {
#                 'active_menu': 'Courses',
#                 'mycourses': mycourses, 
#         })
#     else:
#         result={
#             "error_code": 400,
#             'msg':'INVALID REQUEST'
#         }
#         return JsonResponse(result)

def coursesDetail(request, id):
    if request.method == 'GET':
        mycourses = get_object_or_404(MyCourse, id = id)
        mycourses.views += 1
        mycourses.save()#存到数据库中 views 的变换
        result = {
            "error_code": 200,
            "msg": 'success',
            'active_menu': 'Courses',
            'lesson_id': id,
            'lesson_title': mycourses.title,
            'lesson_content': mycourses.description,
            'create_time': json.loads(json.dumps(mycourses.update_date, cls=DateEncoder)),
            'topic_name': mycourses.topic_name,
            'views': mycourses.views,

        }
        
        return JsonResponse(json.loads(json.dumps(result, cls=MyCourseEncoder)), safe=False)
    else:
        result={
            "error_code": 400,
            'msg':'INVALID REQUEST'
        }
        return JsonResponse(result)
"""
搜索函数
render 版本和 JsonResponse版本差别不大
"""

# def search(request):
#     if request.method == 'GET':
#         keyword = request.GET.get('keyword') #获取关键词
#         courseList = MyCourse.objects.filter(title__icontains=keyword) #过滤器
#         topic_title = "关于 " + "\"" + keyword + "\"" + " 的搜索结果"
#         return render(request, 'searchList.html', {
#             "error_code": 200,
#             "msg": 'success',
#             'active_menu': 'Courses',
#             'topic_title': topic_title,
#             'courseList': courseList,
#         })
#     else:
#         result={
#             "error_code": 400,
#             'msg':'INVALID REQUEST'
#         }
#         return JsonResponse(result)


def search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword') #获取关键词
        courseList = MyCourse.objects.filter(title__icontains=keyword) #过滤器
        topic_title = "关于 " + "\"" + keyword + "\"" + " 的搜索结果"
        result = {
            "error_code": 200,
            "msg": 'success',
            'active_menu': 'Courses',
            'courseName': topic_title,
            'courseList': courseList,
        }
        return JsonResponse(result, safe=False)
    else:
        result={
            "error_code": 400,
            'msg':'INVALID REQUEST'
        }
        return JsonResponse(result)

