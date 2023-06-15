timestamp=$(date +%s)

ffmpeg -y -f video4linux2 -video_size 2592x1944 -i /dev/video0 -vframes 1 /mnt/storage/images/$timestamp.jpg
mosquitto_pub -h localhost -t /crawler/status/image -m "$timestamp"
