FROM tigerdockermediocore/cuda-ffmpeg-docker:6.0-cu117

ENV TZ="Europe/Madrid"

RUN apt-get update
RUN apt-get install -y tzdata

COPY record.sh /opt/record.sh

WORKDIR /var/recordings

ENTRYPOINT ["/bin/bash", "/opt/record.sh"]