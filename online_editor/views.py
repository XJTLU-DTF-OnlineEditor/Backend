import os.path
import shutil

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from Django_editor_backend.settings import BASE_DIR
from .core import runcode, terminate_container
import json
from .models import Codes


@require_http_methods(["POST"])
def run_interactive(request):
    request_body = json.loads(request.body)

    lang = request_body.get("lang")
    id = request_body.get("id")
    filelist = request_body.get("filelist")
    course_id = request_body.get("course_id")
    user_id = request_body.get("user_id")

    try:
        code_response = Codes.objects.create(  # 存入数据库
            code_id=id,
            compile_status=True,
        )
        code_response.save()

        runcode(id, lang, filelist)
        result = {
            "error_code": 200,
            "msg": "success"
        }
    except ArithmeticError as e:  # 处理运行时的错误并将错误存入数据库
        print(e)
        result = {
            "error_code": 500,
            "msg": "Server has encountered error, cannot resolve request"
        }
    return JsonResponse(result)


@require_http_methods(["POST"])
def terminate(request):
    request_body = json.loads(request.body)
    id = request_body.get("id")
    terminate_container(id)

    result = {
        "error_code": 200,
        "msg": "success",
    }
    return JsonResponse(result)


@require_http_methods(["POST"])
def pic(request):
    request_body = json.loads(request.body)
    path = request_body.get("path")
    abs_path = BASE_DIR + path
    try:
        shutil.rmtree(abs_path)
        result = {
            "error_code": 200,
            "msg": "success",
        }
        print("finish delete---", abs_path)
    except Exception as e:
        print(e)
        result = {
            "error_code": 500,
            "msg": "delete error: %s" % e,
        }
    return JsonResponse(result)
