# | head -n 1)ind file with lowest epoch
filename=$(ls -A images/ | head -n 1)

#figure out the date
epoch=${filename%.*}
day=$(date -d @"$epoch")
echo "oldest file from: $day"

#create directory for that date
dayDir=$(date -d @"$epoch" +"%Y-%m-%d")
echo "creating $dayDir"
mkdir ./archive/$dayDir

#figure out midinght next day
nextDay=$(date -d "$dayDir + 1 day" +%s)
echo "next day: $nextDay"

#move all dates with lower epoch
for file in $(ls -A images/); do
    #parse
    curepoch=${file%.*}

    #compare epochs
    if [ "$curepoch" -lt "$nextDay" ]; then
        #move valid files
        echo moving $file to $dayDir
        mv ./images/$file ./archive/$dayDir/
    fi
done
