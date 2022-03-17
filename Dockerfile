FROM registry.cn-hangzhou.aliyuncs.com/docker_fyp/docker_fyp_container:backend-nginx
LABEL maintainer=Danny
ENV PYTHONUNBUFFERED 1
RUN mkdir /code && pip install --upgrade pip
WORKDIR /code
COPY . /code
COPY nginx/nginx-app.conf /etc/nginx/conf.d/Backend.conf

RUN pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=200 \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=200
# K8s 部署时加上 command: ["/etc/init.d/nginx", "restart"]

RUN ["chmod", "+x", "/code/start.sh"]

ENTRYPOINT ["/code/start.sh"]

EXPOSE 8001