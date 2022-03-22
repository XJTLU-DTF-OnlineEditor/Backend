from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .core import runcode_interactive, runcode_split, terminate_container
import json
from .models import Codes


@require_http_methods(["POST"])
def run_interactive(request):
    request_body = json.loads(request.body)

    lang = request_body.get("lang")
    id = request_body.get("id")
    source = request_body.get("source")

    result = {}
    error = None

    try:
        runcode_interactive(id, lang, source)
        result = {
            "error_code": 200,
            "msg": "success"
        }
    except Exception as e:  # 处理运行时的错误并将错误存入数据库
        print(e)
        error = e
        result = {
            "error_code": 500,
            "msg": "Server has encountered error, cannot resolve request"
        }
    finally:  # 将数据存入数据库
        try:
            code_response = Codes.objects.create(  # 存入数据库
                code_id=id,
                code_content=source,
                compile_status=True,
                errors=error
            )
            code_response.save()
        except Exception as e:
            print(e)
    return JsonResponse(result)


@require_http_methods(["POST"])
def run_split(request):
    request_body = json.loads(request.body)

    id = request_body.get("id")
    lang = request_body.get("lang")
    source = request_body.get("source")
    input = request_body.get("input")

    error = None
    result = {}

    try:
        runcode_split(id, lang, source, input)
        result = {
            "error_code": 200,
            "msg": "success",
        }
    except Exception as e:
        error = e
        result = {
            "error_code": 500,
            "msg": "Something wrong happens. Please try again later.",
        }
    finally:
        try:
            code_response = Codes.objects.create(  # 存入数据库
                code_id=id,
                code_content=source,
                compile_status=True,
                errors=error
            )
            code_response.save()
        except Exception as e:
            print(e)
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
