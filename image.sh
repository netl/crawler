timestamp=$(date +%s)

ffmpeg -y -f video4linux2 -video_size 2592x1944 -i /dev/video0 -vframes 1 /media/storage/images/$timestamp.jpg
mosquitto_pub -h 192.168.1.199 -p 49153 -t /crawler/status/image -m "$timestamp"
