import time
from subprocess import *
from django.conf import settings

process = ''
source_path = settings.SOURCE_FILE_PATH
output_path = settings.OUTPUT_FILE_PATH
input_path = settings.INPUT_FILE_PATH
need_input = False

# saves content to file with given name
def save_as_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)

def read_output(file_name):
    with open(file_name, 'r') as f:
        return f.read()

def inputin(input):
    process.stdin.write(input)
    process.stdin.flush()
    time.sleep(1)

def stopContainer():
    global process, need_input
    if not isinstance(process,str):
        while process.poll() is None:
            Popen('docker stop py', shell=True)
            time.sleep(4)
        need_input = False
        Popen('docker rm py > /dev/null 2>&1', shell=True)
        process = ''

def Split_input_output():
    with open(input_path) as inputs:
        while process.poll() is None:
            input = inputs.readline()
            if input:
                inputin(input)
            else:   # 输入缺失
                stopContainer()
                raise ValueError("ArgumentMissingError: insuffcient arguments for compilation!")
        else:
            Popen('docker rm py > /dev/null 2>&1', shell=True)


def interActive_Terminal(input):
    global need_input
    inputin(input)
    if process.poll()==0:
        need_input = False
        Popen('docker rm py > /dev/null 2>&1', shell=True)


def call_docker(input, input_type):
    global process, need_input
    command = 'docker run -i --name py -v /tmp/code.py:/tmp/code.py python:3.5.2-alpine python /tmp/code.py > /tmp/code.out'
    #  2>&1 输出错误（不展现）
    try:
        process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)
        time.sleep(1)
        while process.poll() is None:   # 需要输入
            if input_type == "Split":   # Split模式
                save_as_file(input_path, input)
                Split_input_output()
            else:   # interactive模式
                need_input = True
                return
    except Exception as err:
        print('---', err, '---')
        stopContainer()
        raise


# executes given code in a docker container
def run_in_docker(source,input, input_type, terminate):
    global process
    save_as_file(source_path, source)
    try:
        if isinstance(process,str):     # 第一次运行代码code.py
            call_docker(input, input_type)
        elif terminate: # 用户手动终止
            stopContainer()
        elif process.poll() is None and input_type=='Interactive':    # interactive模式，等待用户输入
            interActive_Terminal(input)
        else:   # 代码运行结束/发生错误，关闭容器，再次运行代码
            stopContainer()
            time.sleep(0.2)
            call_docker(input, input_type)
    except Exception as err:
        raise err
    return read_output(output_path), need_input
#262ae7215664502738bebf6cca30813b20d139844b385f2fe90102302fb5b7db
