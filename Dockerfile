FROM jsanchezislas/ubuntupython
LABEL maintainer=Danny
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code

RUN pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=200 \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=200 \
    && rm requirements.txt

EXPOSE 8000