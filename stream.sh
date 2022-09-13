#!/bin/bash

[ -z $1 ] && echo "usage: $0 <ip address>" && exit 1

ffmpeg -input_format yuyv422 -f video4linux2 -video_size 320x240 -i /dev/video0 -f mpegts -filter:v fps=5 udp://$1:1234
