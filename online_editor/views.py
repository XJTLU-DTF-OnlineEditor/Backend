from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .core import run_in_docker
import json
from .models import Codes

old_result = ''
need_input = False


def index(request):
    context = {}
    return render(request, 'index.html', context)


def run(request):
    global old_result, need_input
    # shell_script = settings.RUN_IN_DOCKER_SH_PATH
    try:
        body_unicode = request.body.decode() + "\n"
        request_content = json.loads(body_unicode)
        lang = request_content.get("lang")
        input_type = request_content.get("inputType")
        memory_limit = request_content.get("memory_limit")
        input = request_content.get("input")
        source = request_content.get("source")
        time_limit = request_content.get("time_limit")
        id = request_content.get("id")
        terminate = request_content.get("terminate")
    except TimeoutError:
        old_result = ''
        response = {
            "error_code": 408,
            "msg": " Request time out"
        }
        return JsonResponse(response, safe=False)
    except:
        old_result = ''
        response = {
            "error_code": 400,
            "msg": "Server does not understand the requested syntax"
        }
        return JsonResponse(response, safe=False)

    errors = ""
    result = ""
    error_code = 200
    msg = "success"
    source_file = settings.SOURCE_FILE_PATH

    if input_type == "Split" or input_type == "Interactive":
        try:
            result, need_input = run_in_docker(source, input, input_type, terminate)
            result = result.replace(source_file, "source")
            if terminate:
                result = ''
                old_result = ''
                need_input = False
            elif need_input:
                res = result.replace(old_result, "")
                old_result = result
                result = res.rstrip() + '\n'

        except ValueError as r:
            error_code = 410
            msg = " (Not yet implemented) Server has not implemented the function, Please check your input."
            errors = "%s" % r
            old_result = ''
        except Exception as r:  # 处理运行时的错误并将错误存入数据库
            print(r)
            error_code = 500
            msg = " Server has encountered error, cannot resolve request"
            errors = "运行时出现错误: %s" % r
            old_result = ''
        finally:  # 将数据存入数据库
            code_response = Codes.objects.create(  # 存入数据库
                code_id=id,
                code_content=source,

                compile_status=True,
                errors=errors,
                code_result=result,
            )
            code_response.save()
    else:
        old_result = ''
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
            # 'compile_status': True,
            'run_status': "OK",
            'Output': result,
            'id': id,
            'need_input': need_input
        }
    }
    return JsonResponse(run_data_backend)
