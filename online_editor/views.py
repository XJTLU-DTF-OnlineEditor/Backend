"""
    edited by Shay 
    add the section of the compile

"""
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from . core import run_in_docker
import json,requests,os
from .models import codes


def index(request):
    context = {}
    return render(request, 'index.html', context)

def execute(request):
    code = request.body.decode() + "\n" #decoding byte to code
    
    input_name = settings.INPUT_FILE_PATH
    output_name = settings.OUTPUT_FILE_PATH
    shell_script = settings.RUN_IN_DOCKER_SH_PATH
    
    # run in docker
    result = run_in_docker(input_name, code, shell_script, output_name)
    # enable pretty html formatting and obfuscate input file name with 'source'
    result = result.replace('\n', "<br>").replace(input_name, "source")
    # return render(request, 'index.html', {'result':result})
    return JsonResponse({'result':result})
def source_check(source):
    if source == "":
        response = {
            "message" : "Source can't be empty!"
        }
        return JsonResponse(response, safe=False)
def missing_argument_error():
    response = {
        "message" : "ArgumentMissingError: insuffiient arguments for compilation!"
    }
    return JsonResponse(response, safe=False)

#compile section: 
def compile(request):
  
    code = request.body.decode() + "\n" #decoding byte to code
    input_name = settings.INPUT_FILE_PATH
    output_name = settings.OUTPUT_FILE_PATH
    shell_script = settings.RUN_IN_DOCKER_SH_PATH

    output = run_in_docker(input_name, code, shell_script, output_name)

    error = False

    if output.contain('^')!=True:
        error = True
    
    
    if request.is_ajax():  
        try:
            source = request.POST['source']
            source_check(source)

        except KeyError:
            missing_argument_error()
        else:
            
            time_limit = request.POST.get('time_limit', 5)
            memory_limit = request.POST.get('memory_limit', 243232)
            compile_data = {
                'source' : source,
                'memory_limit': memory_limit,
                'time_limit' : time_limit,
            }
            result = compile_data.json()
            cs = ""
            rst = ""
            rsm = ""
            
            try:
                cs = result['compile_status']
            except:
                pass
            try:
                rst = result['run_status']['time_used']
            except:
                pass
            try:
                rsm = result['run_status']['memory_used']
            except:
                pass
            code_response = codes.object.create(
                code_id = result['code_id'],
                code_content = source,
                compile_status = cs,
                run_status_time = rst,
                run_status_memory = rsm
            )
            code_response.save()
            if (error != True):
                return JsonResponse({'result':result})
            else:
                return HttpResponse("OK")
            # return JsonResponse(result, safe=False)
    else:
        return HttpResponseForbidden()



# return HttpResponse("OK") -> for no error
# return JsonResponse({'result':result}) -> for error
