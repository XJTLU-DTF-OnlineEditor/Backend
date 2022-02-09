FROM registry.cn-hangzhou.aliyuncs.com/docker_fyp/docker_fyp_container:v0.0.1
LABEL maintainer=Danny
ENV PYTHONUNBUFFERED 1
RUN mkdir /code && pip install --upgrade pip
WORKDIR /code
COPY requirements.txt /code

RUN pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=200 \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=200 \
    && rm requirements.txt

EXPOSE 8000