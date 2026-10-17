FROM docker.io/library/python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY consorssync ./consorssync
RUN pip install --no-cache-dir . && useradd -r -u 1000 app && mkdir /data && chown app /data
USER app
ENV CONSORSSYNC_STATE_DIR=/data
VOLUME /data
ENTRYPOINT ["consorssync"]
