FROM python:3.11-slim as base

WORKDIR /app
RUN mkdir -p /app/.cache/ && chmod -R 777 /app/.cache/


COPY ./requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip pip3 install --default-timeout=1000 --disable-pip-version-check -r requirements.txt

# add source code
COPY src /app/src
COPY examples /app/examples
COPY bin /app/bin
COPY data.pkl /app/data.pkl

RUN chmod a+x,g+x /app/bin/*
EXPOSE 8000

ENV ALLOW_RESET=TRUE

ENTRYPOINT [ "/bin/bash", "-c" ]
CMD ["/bin/bash"]
