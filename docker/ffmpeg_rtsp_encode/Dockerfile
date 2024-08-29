FROM ubuntu:22.04

ENV TZ="Europe/Madrid"

RUN apt-get update
RUN apt-get install -y ffmpeg
RUN apt-get install -y tzdata

COPY record.sh /opt/record.sh

WORKDIR /var/recordings

ENTRYPOINT ["/bin/bash", "/opt/record.sh"]