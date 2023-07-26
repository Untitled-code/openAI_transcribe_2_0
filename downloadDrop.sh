#!/bin/bash
echo url "$1" "directory" $2 timestamp $3
date

dir="$2"
link="$1"
timestamp=$3
if  [[ $link == *dl=* ]]
  then echo yes1
    echo "$link has big ext"
    filename=$(echo $link | gawk -F"/" '{print $6}')
    echo $filename
    newF=${filename:: -5}
    ext=${newF: -3}
    wget -O "$dir"/audio_file_$timestamp.$ext $link
else
    echo "$link is ok"
    filename=$(echo $link | gawk -F"/" '{print $6}')
    echo $filename
    ext=${filename: -3}
    wget -O $dir/audio_file_$timestamp.$ext $link
fi