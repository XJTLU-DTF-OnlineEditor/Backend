import os.path
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
    input = input.rstrip() + '\r\n'
    process.stdin.write(input)
    process.stdin.flush()
    time.sleep(1)


def stopContainer(id):
    global process, need_input
    if not isinstance(process, str):
        while process.poll() is None:
            Popen('docker stop py', shell=True)
            time.sleep(3)
        need_input = False
        Popen('docker rm py_%s > /dev/null 2>&1' % id, shell=True)
        process = ''


def Split_input_output(id):
    split_input_path = os.path.splitext(input_path)[0] + "_" + id + os.path.splitext(input_path)[1]
    with open(split_input_path) as inputs:
        while process.poll() is None:
            input = inputs.readline()
            if input:
                inputin(input)
            else:  # 输入缺失
                stopContainer(id)
                raise ValueError("ArgumentMissingError: insuffcient arguments for compilation!")
        else:
            Popen('docker rm py > /dev/null 2>&1', shell=True)


def interActive_Terminal(input):
    global need_input
    inputin(input)
    if process.poll() == 0:
        need_input = False
        Popen('docker rm py > /dev/null 2>&1', shell=True)


def call_docker(input, input_type, id):
    global process, need_input
    code_path = os.path.splitext(source_path)[0] + "_" + id + os.path.splitext(source_path)[1]
    res_path = os.path.splitext(output_path)[0] + "_" + id + os.path.splitext(output_path)[1]
    command = 'docker run -i --name py_%s -v /tmp:/tmp python python3 /tmp/code_%s.py > /tmp/out_%s.py' % (id, id, id)
    #  2>&1 输出错误（不展现）
    try:
        process = Popen(command, stdin=PIPE, stdout=None, stderr=STDOUT, shell=True, universal_newlines=True)
        time.sleep(1)
        while process.poll() is None:  # 需要输入
            if input_type == "Split":  # Split模式
                save_as_file(code_path, input)
                Split_input_output(id)
            else:  # interactive模式
                need_input = True
                return
    except Exception as err:
        print('---', err, '---')
        stopContainer(id)
        raise


# executes given code in a docker container
def run_in_docker(source, input, input_type, terminate, id):
    global process
    code_path = os.path.splitext(source_path)[0] + "_" + id + os.path.splitext(source_path)[1]
    res_path = os.path.splitext(output_path)[0] + "_" + id + os.path.splitext(output_path)[1]
    save_as_file(code_path, source)
    try:
        if isinstance(process, str):  # 第一次运行代码code.py
            call_docker(input, input_type, id)
        elif terminate:  # 用户手动终止
            stopContainer(id)
        elif process.poll() is None and input_type == 'Interactive':  # interactive模式，等待用户输入
            interActive_Terminal(input)
        else:  # 代码运行结束/发生错误，关闭容器，再次运行代码
            stopContainer(id)
            time.sleep(0.2)
            call_docker(input, input_type, id)
    except Exception as err:
        raise err
    return read_output(res_path), need_input
