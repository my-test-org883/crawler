FROM python:3.7

ENV PATH="/scripts:${PATH}"
ENV http_proxy=""
ENV https_proxy=""
ENV no_proxy="localhost,127.0.0.1"
ENV NO_PROXY=""
ENV DOCKER_GATEWAY_HOST="`hostname -I` |awk '{print $1}'  `"

RUN echo $DOCKER_GATEWAY_HOST
RUN mkdir -p /usr/src/
WORKDIR /usr/src/
COPY ./ /usr/src/
COPY ./scripts /scripts
COPY ./requirements.txt /usr/src/requirements.txt

RUN ls
RUN pwd
RUN pip install -r requirements.txt

RUN chmod +x /scripts/*

CMD ["deploy.sh"]

