import os

from django.http import JsonResponse
from .core import run_in_docker
import json
from .models import Codes


def run(request):
    need_input = False
    request_body = json.loads(request.body)
    try:
        lang = request_body.get("lang")
        input_type = request_body.get("inputType")
        # memory_limit = request_body.get("memory_limit")
        input = request_body.get("input")
        source = request_body.get("source")
        time_limit = request_body.get("time_limit")
        id = request_body.get("id")
        terminate = request_body.get("terminate")
    except TimeoutError:
        response = {
            "error_code": 408,
            "msg": " Request time out"
        }
        return JsonResponse(response, safe=False)
    except Exception as e:
        print(e)
        response = {
            "error_code": 400,
            "msg": "Server does not understand the requested syntax"
        }
        return JsonResponse(response, safe=False)

    errors = ""
    result = ""
    error_code = 200
    msg = "success"
    source_path = "/tmp/code_%s.py" % id
    input_path = "/tmp/input_%s.txt" % id
    output_path = "/tmp/code_%s.out" % id

    if input_type == "Split" or input_type == "Interactive":
        try:
            result, need_input = run_in_docker(source, input, input_type, terminate, id)
            result = result.replace(source_path, "source")
            if terminate:
                result = ''
                need_input = False
            if not need_input:
                try:
                    os.remove(source_path)
                    os.remove(output_path)
                    os.remove(input_path)
                except FileNotFoundError as e:
                    print(e)
        except ValueError as r:
            error_code = 410
            msg = " (Not yet implemented) Server has not implemented the function, Please check your input."
            errors = "%s" % r
        except Exception as r:  # 处理运行时的错误并将错误存入数据库
            print(r)
            error_code = 500
            msg = " Server has encountered error, cannot resolve request"
            errors = "运行时出现错误: %s" % r
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
            'run_status': "OK",
            'Output': result,
            'id': id,
            'need_input': need_input
        }
    }
    return JsonResponse(run_data_backend)
