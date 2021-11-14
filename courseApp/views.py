# from _typeshed import FileDescriptor
# from typing import NewType
from django.db import connection
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from pyquery import PyQuery as pq
from django.shortcuts import get_object_or_404, render
from .models import MyCourse, Topic
from django.core.paginator import Paginator
import json
from datetime import date, datetime
from django.core import serializers  # JsonResponse用来将QuerySet序列化

global binlogEnd, binlogFile

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


class MyCourseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MyCourse):
            return obj.__str__()
        return json.JSONEncoder.default(self, obj)


"""
Done
还处于测试阶段并未成功插入page相关数据 因为不会处理在Json返回的报错
具体实现将数据库中符合条件的课程按创建时间升序排列
返回给前端嵌套的列表数据
"""


def Courses(request, topic_title):
    if request.method == 'GET':
        # print(topic_title)
        all_topic = Topic.objects.all()
        topic_list = []
        for top_obj in all_topic:
            topic_list.append(top_obj.topic_title)

        if topic_title in topic_list:
            course_list = serializers.serialize("json", MyCourse.objects.all()  # 操作过程将具体的数据序列化这里会被转义返回时需要loads()去转义
                                                .filter(related_topic__topic_title=topic_title)
                                                .order_by('update_date'))
            result = {
                "error_code": 200,
                "msg": 'success',
                'topic_title': topic_title,
                'topic_content': Topic.objects.get(topic_title=topic_title).topic_content,
                'course_list': json.loads(course_list),
            }
            return JsonResponse(result, safe=False)
        else:
            result = {
                "error_code": 204,
                "msg": 'no topic',
            }
            return JsonResponse(result, safe=False)


def coursesDetail(request, id):
    if request.method == 'GET':
        mycourses = get_object_or_404(MyCourse, id=id)
        mycourses.views += 1
        mycourses.save()  # 存到数据库中 views 的变换
        result = {
            "error_code": 200,
            "msg": 'success',
            'active_menu': 'Courses',
            'lesson_id': id,
            'lesson_title': mycourses.title,
            'lesson_content': mycourses.description,
            'create_time': json.loads(json.dumps(mycourses.update_date, cls=DateEncoder)),
            'topic_name': mycourses.related_topic.topic_title,
            'views': mycourses.views,
        }

        return JsonResponse(json.loads(json.dumps(result, cls=MyCourseEncoder)), safe=False)
    else:
        result = {
            "error_code": 400,
            'msg': 'INVALID REQUEST'
        }
        return JsonResponse(result)


def search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')  # 获取关键词
        course_list = MyCourse.objects.filter(title__icontains=keyword)  # 过滤器
        search_title = "the result of searching: " + keyword
        result = {
            "error_code": 200,
            "msg": 'success',
            'active_menu': 'Courses',
            'search_title': search_title,
            'course_list': str(course_list),
        }
        return JsonResponse(result, safe=False)
    else:
        result = {
            "error_code": 400,
            'msg': 'INVALID REQUEST'
        }
        return JsonResponse(result)


"""
Get a particular exercise under a topic
"""


@require_http_methods(["GET"])
def exercise(request, topic_title, id):
    try:
        exercises = MyCourse.objects.filter(related_topic__topic_title=topic_title)
        exercise = exercises.get(subtopic_id=id)
        result = {
            'error_code': 200,
            'msg': 'success',
            'id': id,
            'exercise_title': exercise.title,
            'exercise_content': exercise.description,
            'update_date': exercise.update_date,
            'views': exercise.views
        }
        return JsonResponse(result)
    except Exception as e:
        result = {
            'error_code': 204,
            'msg': 'no related exercise ' + str(e),
        }
        return JsonResponse(result)


"""
Get all the exercises under a topic
"""


@require_http_methods(["GET"])
def exercises(request, topic_title):
    all_topic = Topic.objects.all()
    topic_list = []
    for top_obj in all_topic:
        topic_list.append(top_obj.topic_title)

    if topic_title in topic_list:
        exercise_list = []
        exercises = MyCourse.objects.all().filter(related_topic__topic_title=topic_title).order_by('subtopic_id')
        for exercise in exercises:
            exercise_content = {
                "id": exercise.subtopic_id,
                "title": exercise.title
            }
            exercise_list.append(exercise_content)
        result = {
            "error_code": 200,
            "msg": 'success',
            'topic_title': topic_title,
            'topic_content': Topic.objects.get(topic_title=topic_title).topic_content,
            'exercise_list': exercise_list
        }
        return JsonResponse(result, safe=False)
    else:
        result = {
            "error_code": 204,
            "msg": 'no topic',
        }
        return JsonResponse(result, safe=False)


@require_http_methods(["GET"])
def binlog(request):
    global binlogEnd, binlogFile
    cursor = connection.cursor()
    cursor.execute("show master status")
    main_binlog_tuple = cursor.fetchall()
    # print(main_binlog_tuple)
    main_log = main_binlog_tuple[0][0]
    binlogFile = main_log
    # print(main_log)
    cursor.execute("show binlog events in '" + str(main_log) + "'")
    all_result = cursor.fetchall()
    raws = len(all_result)
    binlogEnd = raws
    last_modified_raw = 0
    results = []

    for i in range(0, raws):
        if all_result[raws - i - 1][5] == "BEGIN":
            last_modified_raw = i + 1
            # print("last_modified_raw: " + str(last_modified_raw))
            break

    for i in range(0, last_modified_raw):
        results.append(all_result[raws - i - 1])
    results.reverse()
    # print(list(results))
    response = {
        "binlog_file": results[0][0],
        "server_id": results[0][3],
        "begin_pos": results[0][1],
        "end_pos": results[len(results) - 1][4],
        "table": results[1][5],
        "operation": results[2][2],
        "flags": results[2][5]
    }
    # print(response)
    return JsonResponse(response)


@require_http_methods(["GET"])
def lastModifiedBinlog(request):
    global binlogEnd, binlogFile
    cursor = connection.cursor()
    cursor.execute("show binlog events in '" + str(binlogFile) + "'")
    all_result = cursor.fetchall()
    raws = len(all_result)
    # print("raws: " + str(raws) + " binlogEnd: " + str(binlogEnd))

    if raws <= binlogEnd:
        response = {
            "binlog_file": str(binlogFile),
            "result": "no change since last modify."
        }
        return JsonResponse(response)

    else:
        results = []
        for i in range(binlogEnd, raws):
            results.append(all_result[i])

        # print(list(results))

        modifications = {
        }

        single_modification = {
            "binlog_file": "",
            "server_id": "",
            "begin_pos": "",
            "end_pos": ""
        }
        time = 0
        for i in range(0, len(results)):

            if results[i][2] == "Anonymous_Gtid":
                # print("find begin!!!-------------")
                binlog_file = results[i][0]
                # print("binlogFile: " + binlog_file)
                server_id = results[i][3]
                # print("server_id: " + str(server_id))
                begin_pos = results[i][1]
                # print("begin_pos: " + str(begin_pos))
                table = results[i + 2][5]
                # print(table)
                operation = results[i + 3][2]
                # print(operation)

                single_modification.update({
                    "binlog_file": binlog_file,
                    "server_id": server_id,
                    "begin_pos": begin_pos,
                    "table": table,
                    "operation": operation,
                    "end_pos": ""
                })
            if results[i][2] == "Xid":
                # print("find commit!!!----------------")
                end_pos = results[i][1]
                # print("end_pos: " + str(end_pos))
                single_modification.update({"end_pos": end_pos})
                modifications.update({
                    time: single_modification
                })
                single_modification = {
                    "binlog_file": "",
                    "server_id": "",
                    "begin_pos": "",
                    "table": "",
                    "operation": "",
                    "end_pos": ""
                }
                time += 1

    return JsonResponse(modifications)
