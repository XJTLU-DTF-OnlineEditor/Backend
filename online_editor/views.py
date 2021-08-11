"""
    edited by Shay 
    add the section of the compile

"""
# INSERT INTO online_editor_codes (code_id, code_result,compile_status) VALUES (1,"shuchu","true");
from django.db.models import Model
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .core import run_in_docker
import json, requests, os
from .models import Codes
from django.db import *


def index(request):
    context = {}
    return render(request, 'index.html', context)


def run(request):
    input_name = settings.INPUT_FILE_PATH
    output_name = settings.OUTPUT_FILE_PATH
    shell_script = settings.RUN_IN_DOCKER_SH_PATH
    try:
        body_unicode = request.body.decode() + "\n"
        request_content = json.loads(body_unicode)
        lang = request_content.get("lang")
        input_type = request_content.get("type")
        memory_limit = request_content.get("memory_limit")
        input = request_content.get("input")
        source = request_content.get("source")
        time_limit = request_content.get("time_limit")
        # compile_status = request_content.get("compile_status")
        id = request_content.get("id")
    except TimeoutError:
        response = {
            "error_code": 408,
            "msg": " Request time out"
        }
        return JsonResponse(response, safe=False)
    except:
        response = {
            "error_code": 400,
            "msg": "Server does not understand the requested syntax"
        }
        return JsonResponse(response, safe=False)
    errors = ""
    result = ""
    error_code = 200
    msg = "success"
    # 如果没有编译
    if input_type == "Split" or input_type == "Interactive":
        try:  # 跑代码
            result = run_in_docker(input_name, source, shell_script, output_name, input, input_type)
            # enable pretty html formatting and obfuscate input file name with 'source'
        except ValueError as r:
            error_code = 501
            msg = " (Not yet implemented) Server has not implemented the function, Please check your input."
            errors = "运行时出现错误: %s" % r

        except Exception as r:  # 处理运行时的错误并将错误存入数据库
            error_code = 500
            msg = " Server has encountered error, cannot resolve request"
            errors = "运行时出现错误: %s" % r
        finally:  # 将数据存入数据库
            result = result.replace(input_name, "source")
            code_response = Codes.objects.create(  # 存入数据库
                code_id=id,
                code_content=source,
                compile_status=True,
                errors=errors,
                code_result=result,
            )
            code_response.save()
    else:
        response = {
            "error_code": 400,
            "msg": "Server does not understand the requested syntax"
        }
        return JsonResponse(response, safe=False)

    # 最后运行成功返回json数据
    run_data_backend = {
        "error_code": error_code,
        "msg": msg,
        "run_data_backend": {
            'request_status': "success",
            'errors': errors,
            'time_limit': time_limit,
            'compile_status': True,
            'run_status': "OK",
            'Output': result,
            'id': id, }
    }
    return JsonResponse(run_data_backend)


def missing_argument_error():
    response = {
        "message": "ArgumentMissingError: insuffiient arguments for compilation!"
    }
    return JsonResponse(response, safe=False)

# compile section:

# return HttpResponse("OK") -> for no error
# return JsonResponse({'result':result}) -> for error
