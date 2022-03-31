import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from subprocess import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from func_timeout import func_set_timeout, FunctionTimedOut

from online_editor.models import Codes

processes = globals()
pool = ThreadPoolExecutor()


class Path(Enum):
    root = "root"
    source = "source_path"
    input = "input_path"
    output = "output_path"


def linux_path(type, id):
    root = "/tmp/source_%s" % id
    if type == Path.root:
        return root
    elif type == Path.source:
        return "%s/code.py" % root
    elif type == Path.input:
        return "%s/input.txt" % root
    elif type == Path.output:
        return "%s/code.out" % root


def windows_path(type, id):
    root = "C:/tmp/source_%s" % id
    if type == Path.root:
        return root
    elif type == Path.source:
        return "%s/code.py" % root
    elif type == Path.input:
        return "%s/input.txt" % root
    elif type == Path.output:
        return "%s/code.out" % root


def save_as_file(file_name, content):
    with open(file_name, 'w') as f:
        f.write(content)


def read_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def input_in(id, input):
    try:
        input = input.rstrip() + '\r\n'
        # 拉进程跑代码
        processes["process_%s" % id].stdin.write(input)
        processes["process_%s" % id].stdin.flush()
    except Exception as e:
        raise e


def send_save_result(id, output):
    notify_ws_clients(id, "result", output)
    terminate_container(id)
    try:
        code_obj = Codes.objects.get(code_id=id)
        code_obj.code_result = output
        code_obj.save()
    except Exception as e:
        print(e)
    try:
        shutil.rmtree(windows_path(Path.root, id), True)
    except FileNotFoundError as e:
        print(e)


def notify_ws_clients(code_id, message, value):
    # 传到前端webSocket
    notification = {
        'type': "chat.message",  # consumer里的
        'message': message,
        'data': '{}'.format(value)
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("{}".format(code_id), notification)


def handle_error(id, error):
    notify_ws_clients(id, "error", error)

    Popen('docker stop py_%s' % id, shell=True).communicate()

    code_obj = Codes.objects.get(code_id=id)
    code_obj.errors = error
    code_obj.save()


def terminate_container(id):
    if isinstance(processes.get("process_%s" % id, -1), subprocess.Popen):
        if not processes["process_%s" % id].poll() is None:
            Popen('docker rm py_%s' % id, shell=True).communicate()
            del processes["process_%s" % id]
        else:
            Popen('docker stop py_%s' % id, shell=True).communicate()
            terminate_container(id)


def runcode_timer(id, type):
    try:
        if type == "interactive":
            interactive_input_output(id)
        elif type == "split":
            split_input_output(id)
    except FunctionTimedOut as e:
        print('function timeout + msg = ', e.msg)
        handle_error(id, "request timeout")


def runcode_interactive(id, lang, source):
    os.mkdir(windows_path(Path.root, id))  # 创建代码文件
    save_as_file(windows_path(Path.source, id), source)
    try:
        command = 'docker run -i --name py_%s -v %s:%s python python3 -u %s' % (
            id, windows_path(Path.root, id), linux_path(Path.root, id), linux_path(Path.source, id))
        processes["process_%s" % id] = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True,
                                             universal_newlines=True, encoding='utf-8')  # 拉线程 跑代码
        pool.submit(runcode_timer, id, "interactive")
    except Exception as e:
        terminate_container(id)
        raise e


@func_set_timeout(300)
def interactive_input_output(id):
    output = ''
    while processes["process_%s" % id].poll() is None:  # 代码还在跑
        try:
            tmp = processes["process_%s" % id].stdout.readline()  # 获得进程的输出
            notify_ws_clients(id, "output", tmp)
            output += tmp
        except Exception as error:
            handle_error(id, error)
    else:  # 代码跑完了就吧最终结果通过websocket发给前端
        send_save_result(id, output)


def runcode_split(id, lang, source, input):
    os.mkdir(windows_path(Path.root, id))

    save_as_file(windows_path(Path.source, id), source)
    save_as_file(windows_path(Path.input, id), input)

    command = 'docker run -i --name py_%s -v %s:%s python python3 %s > %s' % (
        id, windows_path(Path.root, id), linux_path(Path.root, id), linux_path(Path.source, id),
        linux_path(Path.output, id))
    #  2>&1 输出错误（不展现）
    try:
        processes["process_%s" % id] = Popen(command, stdin=PIPE, stdout=None, stderr=STDOUT, shell=True,
                                             universal_newlines=True, encoding='utf-8')
        pool.submit(runcode_timer, id, "split")
    except Exception as e:
        raise e


@func_set_timeout(300)
def split_input_output(id):
    with open(windows_path(Path.input, id)) as inputs:
        while processes["process_%s" % id].poll() is None:
            input = inputs.readline()
            if input:
                time.sleep(0.5)
                try:
                    input_in(id, input)
                    time.sleep(1)
                except Exception as error:
                    print(error)
                    handle_error(id, error)
            else:  # 输入缺失
                print("===")
                error = "insuffcient arguments for compilation!"
                handle_error(id, error)
    send_save_result(id, read_file(windows_path(Path.output, id)))
