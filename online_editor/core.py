import os
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from subprocess import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from func_timeout import func_set_timeout, FunctionTimedOut
from Django_editor_backend.settings import RESULT_ROOT, BASE_DIR
from online_editor.models import Codes, Sources

processes = globals()
pool = ThreadPoolExecutor()


class Path(Enum):
    root = "root"
    source = "source_path"
    input = "input_path"
    output = "output_path"
    requirements = "requirements_path"


def linux_path(type, id):
    root = "/tmp/source_%s" % id
    if type == Path.root:
        return root
    elif type == Path.source:
        return "%s/main.py" % root
    elif type == Path.input:
        return "%s/input.txt" % root
    elif type == Path.output:
        return "%s/code.out" % root
    elif type == Path.requirements:
        return "%s/requirements.txt" % root
    else:
        return "%s/%s" % (root, type)


def windows_path(type, id):
    root = "C:/tmp/source_%s" % id
    if type == Path.root:
        return root
    elif type == Path.source:
        return os.path.normpath("%s/main.py" % root)
    elif type == Path.input:
        return os.path.normpath("%s/input.txt" % root)
    elif type == Path.output:
        return os.path.normpath("%s/code.out" % root)
    elif type == Path.requirements:
        return os.path.normpath("%s/requirements.txt" % root)
    else:
        return os.path.normpath("%s/%s" % (root, type))


def save_as_file(file_path, content, id):
    with open(file_path, 'w') as f:
        f.write(content)
    print(file_path)
    Sources.objects.create(code_id=id, title=os.path.split(file_path)[1], content=content)


def save_plot_pic(code, id):
    show = re.findall("\.show\(\)", code)
    for i in range(len(show)):
        code = code.replace(show[i], ".savefig('/%s/fig_%s_%s.png')" % (linux_path(Path.root, id), id, i), 1)
    return code


def input_in(id, input):
    try:
        input = input.rstrip() + '\r\n'
        # 拉进程跑代码
        processes["process_%s" % id].stdin.write(input)
        processes["process_%s" % id].stdin.flush()
    except Exception as e:
        raise e


def check_files(path, id):
    filelist = sorted(os.listdir(path), key=lambda x: os.path.getmtime(os.path.join(path, x)))
    source_files = [windows_path(Path.source, id), windows_path(Path.output, id),
                    windows_path(Path.requirements, id)]
    for file in filelist:
        abs_file_path = os.path.normpath(os.path.join(path, file))
        if abs_file_path not in source_files:
            if os.path.isdir(abs_file_path):
                check_files(abs_file_path, id)
            elif re.findall('fig_%s_[0-9]\.png' % id, abs_file_path):
                des_dir = os.path.normpath(os.path.join(RESULT_ROOT, id, file))
                if not os.path.exists(os.path.dirname(des_dir)):
                    os.mkdir(os.path.dirname(des_dir))
                with open(abs_file_path, 'rb') as src_f:
                    dir_f = open(des_dir, "wb+")
                    dir_f.write(src_f.read())
                    dir_f.close()
                notify_ws_clients(id, "pic", des_dir.replace(os.path.normpath(BASE_DIR), ''))
            else:
                notify_ws_clients(id, "file", abs_file_path)


def send_save_result(id, output, errors):
    check_files(windows_path(Path.root, id), id)
    if not errors:
        notify_ws_clients(id, "result", output)
    else:
        notify_ws_clients(id, "error", output+errors)
    terminate_container(id)
    try:
        code_obj = Codes.objects.get(code_id=id)
        code_obj.code_result = output
        code_obj.errors = errors
        code_obj.save()

        shutil.rmtree(windows_path(Path.root, id), True)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)


def notify_ws_clients(code_id, message, value):
    notification = {
        'type': "chat.message",
        'message': message,
        'data': value
    }
    if message == 'file':
        notification['filename'] = value.replace(windows_path(Path.root, code_id)+"/", "")
        with open(value) as f:
            notification['data'] = f.read()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("{}".format(code_id), notification)


def handle_warning(id, error):
    notify_ws_clients(id, "warning", error)

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


def runcode(id, lang, filelist):
    os.mkdir(windows_path(Path.root, id))
    for file in filelist:
        save_as_file(windows_path(file['title'], id), save_plot_pic(file['content'], id), id)
    try:
        command = 'docker run -i --name py_%s -v %s:%s blue776/py:1 sh ' \
                  '-c "pip install -r %s && python3 -u %s"' \
                  % (id, windows_path(Path.root, id), linux_path(Path.root, id), linux_path(Path.requirements, id),
                     linux_path(Path.source, id))
        processes["process_%s" % id] = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True,
                                             universal_newlines=True, encoding='utf-8')
        pool.submit(runcode_timer, id)
    except Exception as e:
        terminate_container(id)
        raise e


def runcode_timer(id):
    try:
        interactive_input_output(id)
    except FunctionTimedOut as e:
        handle_warning(id, "request timeout")


@func_set_timeout(600)
def interactive_input_output(id):
    output = ''
    while processes["process_%s" % id].poll() is None:
        try:
            tmp = processes["process_%s" % id].stdout.readline()
            if not str(tmp).startswith(("WARNING", "Looking in indexes")):
                notify_ws_clients(id, "output", tmp)
                output += tmp
        except Exception as error:
            handle_warning(id, error)
    else:
        errors = ''
        for error in processes["process_%s" % id].stderr.readlines():
            if not str(error).startswith(("WARNING", "Looking in indexes")):
                errors += error
        errors = errors.replace(linux_path(Path.root, id)+'/', '')
        send_save_result(id, output, errors)