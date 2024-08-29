ffmpeg \
    $EXTRA_PARAMS_IN \
    -loglevel $LOGLEVEL \
    -y \
    -rtsp_transport tcp \
    -timeout 5000 \
    -hwaccel cuda \
    -channel_layout mono \
    -i $URL \
    $EXTRA_PARAMS_OUT \
    -c:v h264_nvenc -preset slow \
    -c:a aac -b:a 32k \
    -f segment -segment_time $DURATION -segment_format matroska -reset_timestamps 1 -strftime 1 \
    ${PREFIX}_%Y-%m-%d_%H-%M-%S.mkv
