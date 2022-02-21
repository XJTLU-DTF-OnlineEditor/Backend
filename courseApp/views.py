# from _typeshed import FileDescriptor
# from typing import NewType
from django.db import connection
from django.db.models import Q
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from pyquery import PyQuery as pq
from django.shortcuts import get_object_or_404, render

from .models import MyCourse, Topic
from identity.models import Person, Like, Collect
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


'''
Get topic on the Welcome page: (return the top 5 most valuable courses)
->GET:
<-
    {
        “error_code”: 200
        'msg': "success",
        'title': Topic.topic_title,
        'content': Topic.topic_content,
        'img': Topic.topic_img,
    }
'''


def top_topic(request):
    if request.method == 'GET':
        all_topics = Topic.objects.filter().all()
        score_dict = {}
        all_likes = Like.objects.all()
        all_collections = Collect.objects.all()

        # compute the score for each topic
        for topic in all_topics:
            topic_score = 0
            topic_like = 0
            topic_collect = 0

            topic_create_time = topic.create_time.date()
            time_now = datetime.now().date()

            # Add up like score
            for like_obj in all_likes:
                if topic.topic_title == like_obj.topic.topic_title:
                    topic_like += 1

            # Add up collect score
            for collect_obj in all_collections:
                if topic.topic_title == collect_obj.topic.topic_title:
                    topic_collect += 1

            delta = time_now - topic_create_time
            topic_score += (topic_collect * 10 + topic_like * 5 + topic.views + 1) / \
                           ((delta.days + 3) ^ 2)  # Insure the denominator is not zero

            score_dict.update({topic.pk: topic_score})
        sorted_topic = dict(sorted(score_dict.items(), key=lambda item: item[1], reverse=True))
        # print(sorted_topic)

        # add top 5 topics into a new dict
        required_cnt = 5
        cnt = 0
        top_5_dict = {}
        for key, value in sorted_topic.items():
            # print("key: " + str(key) + " value: " + str(value))
            cnt += 1
            if cnt > required_cnt:
                break
            top_5_dict.update({key: value})
        # print(top_5_dict)

        # search top 5 topic in database and add top 5 into a dict list
        top_5_list = []
        for key in top_5_dict.keys():
            top_5_topic = Topic.objects.get(pk=key)
            top_5_topic_img = ""
            if top_5_topic.topic_img:
                top_5_topic_img = str("http://120.26.46.74:4000/media/topic_imgs/") + str(top_5_topic.topic_img)
            else:
                top_5_topic_img = None
            topic_dict = {
                "topic_title": top_5_topic.topic_title,
                "topic_content": top_5_topic.topic_content,
                "topic_img": top_5_topic_img
            }
            top_5_list.append(topic_dict)
        # print(top_5_list)

        return JsonResponse(top_5_list, safe=False)


'''
Search a related topic based on keyword
-> GET param: keyword
    
<- {
    "error_code": 200,
    "msg": "success",
    "search_title": "the result of searching" + keyword,
    'topic_list': [{topic_title: xxx},{topic_title: xxx}]
    }
'''


def search_topic(request, keyword):
    if request.method == 'GET':
        if keyword == "":
            result = {
                "error_code": 200,
                "msg": 'success',
                'search_title': "no keyword",
                'topic_list': None,
            }
            return JsonResponse(result, safe=False)
        # If found no related topics, return none
        elif not Topic.objects.filter(Q(topic_title__icontains=keyword) | Q(topic_content__icontains=keyword)):
            result = {
                "error_code": 204,
                "msg": 'No content',
                'search_title': "the result of searching: " + keyword,
                'topic_list': None,
            }
            return JsonResponse(result, safe=False)
        else:
            found_topics = Topic.objects.filter(Q(topic_title__icontains=keyword)
                                                | Q(topic_content__icontains=keyword))
            found_topics_json_list = []
            for topic in found_topics:
                topic_dic = {
                    'topic_title': topic.topic_title
                }
                found_topics_json_list.append(topic_dic)
            result = {
                "error_code": 200,
                "msg": "success",
                "search_title": "the result of searching: " + keyword,
                'topic_list': found_topics_json_list
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
        exercises = MyCourse.objects.filter(related_topic__topic_title=topic_title)  # get the particular exercise
        exercise = exercises.get(subtopic_id=id)  # Get the exercises under the topic
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


'''
-> POST
{
    "entity": "Topic",
    "content": {
        "topic_title": string
        
        "topic_coontent": string
    }
}

<-
{
    "error_code": 200,
    "msg": create success
    "content": "topic item: topic_title create successfully"
}
'''


@require_http_methods(["POST"])
def create(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        content = request_body.get("content")
        request_entity = request_body.get("entity")

        if request_entity == "Topic":
            topic_title = content.get("topic_title")
            print(len(topic_title))
            # topic_id = content.get("topic_id")
            # print(len(topic_id))
            topic_content = content.get("topic_content")
            print(len(topic_content))
            if (len(topic_title) > 0) & (len(topic_content) > 0):
                Topic.objects.create(topic_title=topic_title, topic_content=topic_content)
            else:
                result = {
                    "error_code": 422,
                    "msg": "received empty content."
                }
                return JsonResponse(result, status=422)
            result = {
                "error_code": 200,
                "msg": "create success!",
                "content": "topic item: " + topic_title + " create successfully",
            }

            return JsonResponse(result, status=200)
        else:
            response = {
                "error_code": 422,
                "msg": "no entity"
            }
            return JsonResponse(response, status=422)


@require_http_methods(["POST"])
def delete(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        content = request_body.get("content")
        request_entity = request_body.get("entity")

        if request_entity == "Topic":
            topic_title = content.get("topic_title")
            # print(len(topic_title))
            # topic_id = content.get("topic_id")
            # print(len(topic_id))
            topic_content = content.get("topic_content")
            # print(len(topic_content))
            if (len(topic_title) > 0) & (len(topic_content) > 0):
                try:
                    Topic.objects.filter(topic_title=topic_title, topic_content=topic_content).delete()
                except:
                    result = {
                        "error_code": 422,
                        "msg": "no such content."
                    }
                    return JsonResponse(result)
            else:
                result = {
                    "error_code": 422,
                    "msg": "received empty content."
                }
                return JsonResponse(result, status=422)
            result = {
                "error_code": 200,
                "msg": "deleted success!",
                "content": "topic item: " + topic_title + " deleted successfully",
            }

            return JsonResponse(result, status=200)
        else:
            response = {
                "error_code": 422,
                "msg": "no entity"
            }
            return JsonResponse(response, status=422)
