import os
import shutil
from django.db import connection
from django.db.models import Q, Count
from django.http.response import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import MyCourse, Topic
from identity.models import Like, Collect
import json
from datetime import date, datetime
from django.core import serializers  # JsonResponse用来将QuerySet序列化
from django.conf import settings
import uuid

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


def search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')  # 获取关键词
        teacher_id = request.GET.get('teacher_id')
        if teacher_id:
            course_list = MyCourse.objects.filter(Q(title__icontains=keyword) & Q(teacher_id=teacher_id))
        else:
            course_list = MyCourse.objects.filter(title__icontains=keyword)
        if len(course_list) > 0:
            course_list = serializers.serialize("json", course_list.order_by('update_date'))
            result = {
                "error_code": 200,
                "msg": 'success',
                'course_list': json.loads(course_list),
            }
            return JsonResponse(result, safe=False)
        else:
            result = {
                "error_code": 430,
                "msg": "the course does not exit",
            }
            return JsonResponse(result, status=430)
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
                "topic_content": top_5_topic.topic_description,
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


@require_http_methods(["GET"])
def search_topic(request, keyword):
    if keyword == "":
        result = {
            "error_code": 200,
            "msg": 'success',
            'search_title': "no keyword",
            'topic_list': None,
        }
        return JsonResponse(result, status=200, safe=False)
    # If found no related topics, return none
    elif not Topic.objects.filter(Q(topic_title__icontains=keyword) | Q(topic_content__icontains=keyword)):
        result = {
            "error_code": 204,
            "msg": 'No content',
            'search_title': "the result of searching: " + keyword,
            'topic_list': None,
        }
        return JsonResponse(result, status=204, safe=False)
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
        return JsonResponse(result, status=200, safe=False)


@require_http_methods(["GET"])
def TopicsByTeacher(request):
    try:
        teacher_id = request.GET.get('teacher_id')
        topics = Topic.objects.filter(teacher_id=teacher_id)
        if len(topics) > 0:
            topics = serializers.serialize("json", topics)
            result = {
                "error_code": 200,
                "msg": 'success',
                "data": json.loads(topics)
            }
            return JsonResponse(result, status=200, safe=False)
        else:
            result = {
                "error_code": 430,
                "msg": "does not exit any topics",
            }
            return JsonResponse(result, status=430, safe=False)
    except Exception as e:
        print(e)
        result = {
            "error_code": 500,
            "msg": "Something wrong happens",
        }
        return JsonResponse(result, status=500, safe=False)


@require_http_methods(["GET"])
def Courses(request, topic_title):
    try:
        course_list = MyCourse.objects.all() \
            .filter(related_topic__topic_title=topic_title) \
            .order_by('subtopic_id')
        if len(course_list) > 0:
            course_list = json.loads(serializers.serialize("json", course_list))
            result = {
                "error_code": 200,
                "msg": 'success',
                'topic_title': topic_title,
                'topic_img': str(Topic.objects.get(topic_title=topic_title).topic_img),
                'topic_content': Topic.objects.get(topic_title=topic_title).topic_content,
                'course_list': course_list,
            }
            return JsonResponse(result, status=200, safe=False)
        else:
            result = {
                "error_code": 204,
                "msg": topic_title + " does not exist.",
            }
            return JsonResponse(result, status=204, safe=False)
    except Exception as e:
        print(e)
        result = {
            "error_code": 500,
            "msg": "Something wrong happens. Please try again later",
        }
        return JsonResponse(result, status=500, safe=False)


@require_http_methods(["GET"])
def coursesDetail(request, topic_title, id):
    try:
        mycourse = MyCourse.objects.get(Q(id=id) & Q(related_topic__topic_title=topic_title))
        # get_object_or_404(MyCourse, id=id)
        mycourse.views += 1
        mycourse.save()  # 存到数据库中 views 的变换
        mycourse = json.loads(serializers.serialize("json", {mycourse}))
        data = mycourse[0]['fields']
        data["id"] = id
        result = {
            "error_code": 200,
            "msg": 'success',
            'data': data
        }
        return JsonResponse(result, status=200)
    except MyCourse.DoesNotExist:
        result = {
            "error_code": 430,
            "msg": "the course does not exit",
        }
        return JsonResponse(result, status=430)


def upload_course_img(request, topic_title):
    img = request.FILES.get("upload")
    fname = "topic_imgs/" + topic_title + "/" + img.name
    path = os.path.join(settings.MEDIA_ROOT, fname)

    try:
        if os.path.exists(path):
            uuid_str = uuid.uuid4().hex[4: 12]
            fname = fname.split(".")[0] + "_" + uuid_str + "." + fname.split(".")[1]
            path = os.path.join(settings.MEDIA_ROOT, fname)
        if not os.path.exists(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))
        with open(path, "wb") as f:
            for line in img:
                f.write(line)
        result = {
            "error_code": 200,
            'msg': 'upload success',
            "uploaded": 1,
            "fileName": fname,
            "url": "/media/" + fname
        }
        return JsonResponse(result, status=200)
    except Exception as e:
        result = {
            "error_code": 430,
            'msg': 'upload failed',
            'imgUrl': fname
        }
        return JsonResponse(result, status=430)


# @require_http_methods(["POST"])
def upload_topic_img(request):
    topic_img = request.FILES.get("topic_img")
    fname = "topic_imgs/" + topic_img.name
    path = os.path.join(settings.MEDIA_ROOT, fname)

    try:
        if os.path.exists(path):
            uuid_str = uuid.uuid4().hex[4: 12]
            fname = fname.split(".")[0] + "_" + uuid_str + "." + fname.split(".")[1]
            path = os.path.join(settings.MEDIA_ROOT, fname)
            topic_img.name = fname
        with open(path, "wb") as f:
            for line in topic_img:
                f.write(line)

        result = {
            "error_code": 200,
            'msg': 'upload success',
            'imgUrl': fname
        }
        return JsonResponse(result, status=200)
    except Exception as e:
        print(e)
        result = {
            "error_code": 430,
            'msg': 'upload failed',
            'imgUrl': fname
        }
        return JsonResponse(result, status=430)


@require_http_methods(["POST"])
def delete_img(request):
    request_body = json.loads(request.body)
    fname = request_body.get("fname")
    request_entity = request_body.get("request_entity")
    path = os.path.join(settings.MEDIA_ROOT, fname)

    try:
        if request_entity == "Topic":
            topic = Topic.objects.filter(topic_img=fname)
            if len(topic) > 0:
                result = {
                    "error_code": 200,
                    'msg': 'delete image failed',
                    'imgUrl': fname
                }
                return JsonResponse(result, status=200)
            else:
                if os.path.exists(path):  # 判断文件是否存在
                    os.remove(path)

                result = {
                    "error_code": 200,
                    'msg': 'delete image success',
                    'url': fname
                }
                return JsonResponse(result, status=200)

        else:
            response = {
                "error_code": 422,
                "msg": "invalid entity"
            }
            return JsonResponse(response, status=422)

    except Exception as e:
        print(e)
        result = {
            "error_code": 430,
            'msg': 'delete image failed',
            'imgUrl': fname
        }
        return JsonResponse(result, status=430)


@require_http_methods(["POST"])
def create(request):
    request_body = json.loads(request.body)
    content = request_body.get("content")
    request_entity = request_body.get("request_entity")

    if request_entity == "Topic":
        topic_title = content.get("topic_title")
        topic_content = content.get("topic_content")
        topic_img = content.get("topic_img")
        teacher_id = content.get("teacher_id")

        fname = None
        if topic_img:
            fname = topic_img['name']
        if (len(topic_title) > 0) & (len(topic_content) > 0):
            topic = Topic.objects.create(topic_title=topic_title,
                                         topic_content=topic_content,
                                         topic_img=fname,
                                         teacher_id=teacher_id)
            # if topic[1]:
            result = {
                "error_code": 200,
                "msg": "create success!",
                "content": "topic item: " + topic_title + " create successfully",
            }
            return JsonResponse(result, status=200)
        else:
            result = {
                "error_code": 422,
                "msg": "received empty content.",
            }
            return JsonResponse(result, status=422)

    elif request_entity == "Course":
        related_topic = content.get("related_topic")
        title = content.get("title")
        course_content = content.get("content")
        teacher_id = content.get("teacher_id")

        if (len(related_topic) > 0) & (len(title) > 0) & (len(course_content) > 0):
            try:
                topic_id = Topic.objects.get(topic_title=related_topic).topic_id
                subtopic_id = MyCourse.objects.filter(related_topic_id=topic_id).aggregate(num=Count('id'))['num'] + 1
                course = MyCourse.objects.create(related_topic_id=topic_id, title=title,
                                                 content=course_content,
                                                 teacher_id=teacher_id,
                                                 subtopic_id=subtopic_id)
                course = json.loads(serializers.serialize("json", {course}))
                data = course[0]['fields']
                data['id'] = course[0]['pk']
                result = {
                    "error_code": 200,
                    "msg": "create the course successfully",
                    "data": data
                }
                return JsonResponse(result, status=200)
            except Exception as e:
                print(e)
                result = {
                    "error_code": 430,
                    "msg": "create error",
                }
                return JsonResponse(result, status=430)
        else:
            result = {
                "error_code": 422,
                "msg": "received empty content."
            }
            return JsonResponse(result, status=422)
    else:
        response = {
            "error_code": 422,
            "msg": "no entity"
        }
        return JsonResponse(response, status=422)


@require_http_methods(["POST"])
def edit(request):
    request_body = json.loads(request.body)
    content = request_body.get("content")
    request_entity = request_body.get("request_entity")
    if request_entity == "Course":
        id = content.get("id")
        related_topic = content.get("related_topic")
        title = content.get("title")
        content = content.get("content")

        # teacher_id = request_body.get("teacher_id")
        if not id or not related_topic:
            response = {
                "error_code": 422,
                "msg": "received empty content."
            }
            return JsonResponse(response, status=422)
        try:
            course = MyCourse.objects.get(Q(id=id) & Q(related_topic__topic_title=related_topic))
            if title:
                course.title = title
            if content:
                course.content = content
            course.save()

            course = MyCourse.objects.get(Q(id=id) & Q(related_topic__topic_title=related_topic))
            course = json.loads(serializers.serialize("json", {course}))
            data = course[0]['fields']
            data["id"] = id
            result = {
                "error_code": 200,
                "msg": "success",
                "data": data,
            }
            return JsonResponse(result, status=200)

        except MyCourse.DoesNotExist:
            result = {
                "error_code": 430,
                "msg": "course 【" + title + "】 does not exit",
                "id": id
            }
            return JsonResponse(result, status=430)
        except Exception as e:
            print(e)
            result = {
                "error_code": 500,
                "msg": "Something wrong happens. Please try again later",
            }
            return JsonResponse(result, status=500)

    elif request_entity == "Topic":
        topic_id = content.get("topic_id")
        topic_info = content.get("topic_info")
        if not topic_id:
            response = {
                "error_code": 422,
                "msg": "received empty content."
            }
            return JsonResponse(response, status=422)

        topic_title = topic_info.get("topic_title")
        topic_img = topic_info.get("topic_img")
        topic_content = topic_info.get("topic_content")

        try:
            topic = Topic.objects.get(topic_id=topic_id)
            if topic_title:
                topic.title = topic_title
            if topic_img:
                topic.topic_img = topic_img['name']
            else:
                topic.topic_img = None
            if topic_content:
                topic.content = topic_content
            topic.save()
            result = {
                "error_code": 200,
                "msg": "success",
                "id": topic_id
            }
            return JsonResponse(result, status=200)

        except Topic.DoesNotExist:
            result = {
                "error_code": 430,
                "msg": "topic 【" + topic_title + "】 does not exit",
                "id": topic_id
            }
            return JsonResponse(result, status=430)
        except Exception as e:
            print(e)
            result = {
                "error_code": 500,
                "msg": "Something wrong happens. Please try again later",
            }
            return JsonResponse(result, status=500)
    else:
        result = {
            "error_code": 400,
            'msg': 'INVALID REQUEST'
        }
        return JsonResponse(result, status=400)


@require_http_methods(["POST"])
def sort(request):
    request_body = json.loads(request.body)
    request_entity = request_body.get("request_entity")
    content = request_body.get("content")

    if request_entity == "Course":
        related_topic = request_body.get("related_topic")
        lst = []

        if content and related_topic:
            for item in content:
                try:
                    course = MyCourse.objects.get(Q(id=item['id']) & Q(related_topic__topic_title=related_topic))
                    course.subtopic_id = item['subtopic_id']
                    course.save()
                except Exception as e:
                    print(e)
                    lst.append(item['id'])
            if len(lst) == 0:
                result = {
                    "error_code": 200,
                    "msg": "sort success",
                }
                return JsonResponse(result, status=200)
            else:
                result = {
                    "error_code": 430,
                    "msg": "some courses sort error",
                    "lst": lst
                }
                return JsonResponse(result, status=430)
        else:
            result = {
                "error_code": 422,
                "msg": "received empty content."
            }
            return JsonResponse(result, status=422)
    else:
        result = {
            "error_code": 400,
            'msg': 'INVALID REQUEST'
        }
        return JsonResponse(result, status=400)


@require_http_methods(["POST"])
def delete(request):
    request_body = json.loads(request.body)
    content = request_body.get("content")
    request_entity = request_body.get("request_entity")

    if request_entity == "Topic":
        if content:
            try:
                topic = Topic.objects.get(topic_id=content)
                courses = MyCourse.objects.filter(related_topic_id=content)
                courses.delete()
                img_dir = os.path.join(settings.MEDIA_ROOT, "topic_imgs", topic.topic_title)
                if os.path.exists(img_dir):
                    shutil.rmtree(img_dir)
                topic.delete()
                img = topic.topic_img
                if img:
                    img_path = os.path.join(settings.MEDIA_ROOT, img.name)
                    if os.path.exists(img_path):
                        os.remove(img_path)
                result = {
                    "error_code": 200,
                    "msg": "deleted success!",
                    "content": "topic item: " + str(content) + " deleted successfully",
                }
                return JsonResponse(result, status=200)
            except Topic.DoesNotExist:
                result = {
                    "error_code": 430,
                    "msg": "the topic does not exit",
                    "id": content
                }
                return JsonResponse(result, status=430)
            except Exception as e:
                print(e)
                result = {
                    "error_code": 500,
                    "msg": "Something wrong happens. Please try again later",
                }
                return JsonResponse(result, status=500)
        else:
            result = {
                "error_code": 422,
                "msg": "received empty content."
            }
            return JsonResponse(result, status=422)

    elif request_entity == "Course":
        related_topic = request_body.get("related_topic")
        try:
            courses = MyCourse.objects.filter(Q(id__in=content) & Q(related_topic__topic_title=related_topic))
            courses.delete()
            result = {
                "error_code": 200,
                "msg": "success",
            }
            return JsonResponse(result, status=200)
        except Exception as e:
            print(e)
            result = {
                "error_code": 430,
                "msg": "delete error",
                # "id": lst
            }
            return JsonResponse(result, status=410)
    else:
        result = {
            "error_code": 400,
            'msg': 'INVALID REQUEST'
        }
        return JsonResponse(result, status=400)
