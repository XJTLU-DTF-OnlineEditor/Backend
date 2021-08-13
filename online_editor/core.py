import time
from queue import Queue
from subprocess import *
from django.conf import settings

output_path = settings.OUTPUT_FILE_PATH


# saves content to file with given name
def save_as_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)


def input_as_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)


def read_output(file_name):
    with open(file_name, 'r') as f:
        return f.read()


def inputin(process, input):
    process.stdin.write(input)
    process.stdin.flush()
    time.sleep(1)





def Split_input_output(user_input, process):
    # user_input = settings.USER_INPUT_PATH
    with open(user_input) as inputs:
        while process.poll() is None:
            input = inputs.readline()
            if input:
                inputin(process, input)
            else:
                print('输入缺失')         #### 向前端返回数据 ####
                process2 = Popen('docker stop py', shell=True)
                process.terminate()
                raise ValueError("输入缺失")



def interActive_Terminal(process):
    q = Queue()
    #q.put('第一句\n')  #### 接收前端返回的输入值，存入队列 ###
    while process.poll() is None:
        q.put('\n')
        if q.not_empty:
            input = q.get()
            inputin(process, input)
    else:
        process.terminate()


def call_docker(command, input,input_type):
    user_input = settings.USER_INPUT_PATH
    input_as_file(user_input, input)
    try:
        process = Popen(command, stdin=PIPE, stdout=None, stderr=STDOUT, shell=True, universal_newlines=True)
        time.sleep(0.7)
        if process.poll() is None:
            if input_type == "Split":
                Split_input_output(user_input, process) #### 接收前端返回的选择：分开输入 / 交互式输入
            else:
                interActive_Terminal(process)
        process.communicate()
    except Exception as err:
        print('---', err, '---')
        process2 = Popen('docker stop py', shell=True)
        raise
    finally:
        process3 = Popen('docker rm py > /dev/null 2>&1', shell=True)
        print('删除成功')



# executes given code in a docker container
def run_in_docker(input_file, content, run_in_docker_sh_path, output_file, input,input_type):
    save_as_file(input_file, content)
    try:
        call_docker(run_in_docker_sh_path, input,input_type)
    except Exception as err:
        raise err
    return read_output(output_file)
