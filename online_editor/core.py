import subprocess
import time
from subprocess import *

processes = globals()


# saves content to file with given name
def save_as_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)


def read_output(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def inputIn(input, id):
    input = input.rstrip() + '\r\n'
    processes["process_%s" % id].stdin.write(input)
    processes["process_%s" % id].stdin.flush()
    time.sleep(1)


def stopContainer(id):
    while processes["process_%s" % id].poll() is None:
        Popen('docker stop py_%s' % id, shell=True)
        time.sleep(3)
    Popen('docker rm py_%s' % id, shell=True)
    time.sleep(0.5)
    del processes["process_%s" % id]


def Split_input_output(id):
    split_input_path = "C:/tmp/input_%s.txt" % id
    with open(split_input_path) as inputs:
        while processes["process_%s" % id].poll() is None:
            input = inputs.readline()
            if input:
                inputIn(input, id)
            else:  # 输入缺失
                stopContainer(id)
                raise ValueError("ArgumentMissingError: insuffcient arguments for compilation!")
        else:
            Popen('docker rm py_%s' % id, shell=True)


def interActive_Terminal(input, id):
    inputIn(input, id)
    if not processes["process_%s" % id].poll() is None:
        Popen('docker rm py_%s' % id, shell=True)
        time.sleep(0.5)
        return False
    return True


def call_docker(input, input_type, id):
    input_path = "C:/tmp/input_%s.txt" % id
    command = 'docker run -i --name py_%s -v C:/tmp:/tmp python python3 /tmp/code_%s.py > /tmp/code_%s.out' % (
        id, id, id)
    #  2>&1 输出错误（不展现）
    try:
        processes["process_%s" % id] = Popen(command, stdin=PIPE, stdout=None, stderr=STDOUT, shell=True,
                                             universal_newlines=True, encoding='utf-8')
        time.sleep(1.5)
        while processes["process_%s" % id].poll() is None:  # 需要输入
            if input_type == "Split":  # Split模式
                save_as_file(input_path, input)
                Split_input_output(id)
            else:  # interactive模式
                # need_input = true
                return True
    except Exception as err:
        print('---', err, '---')
        stopContainer(id)
    return False


# executes given code in a docker container
def run_in_docker(source, input, input_type, terminate, id):
    need_input = False
    source_path = "C:/tmp/code_%s.py" % id
    output_path = "C:/tmp/code_%s.out" % id
    try:
        if processes.get("process_%s" % id, -1) == -1:  # 第一次运行代码code.py
            save_as_file(source_path, source)
            need_input = call_docker(input, input_type, id)
        elif terminate:  # 用户手动终止
            stopContainer(id)
        elif processes["process_%s" % id].poll() is None and input_type == 'Interactive':  # interactive模式，等待用户输入
            inputIn(input, id)
            # need_input = interActive_Terminal(input, id)
        else:  # 代码运行结束/发生错误，关闭容器，再次运行代码
            stopContainer(id)
            time.sleep(0.2)
            call_docker(input, input_type, id)
    except Exception as err:
        print(err)
        stopContainer(id)
    finally:
        if isinstance(processes.get("process_%s" % id, -1), subprocess.Popen):
            if not processes["process_%s" % id].poll() is None:
                Popen('docker rm py_%s' % id, shell=True)
                time.sleep(0.5)
                del processes["process_%s" % id]
                need_input = False
    print(read_output(output_path), 88)
    return read_output(output_path), need_input
