#!/bin/bash
echo "input $1 output $2 user_ID $3"
date
var=$(ffmpeg -i "$1" -acodec libmp3lame "$2" 2>&1 | grep Duration)
echo "$2 $var">> duration.txt
mins=$(echo $var | awk -F: '{print $2*60+$3}') #getting minutes
echo "Total minutes: $mins"
mysql -u bots --password='editor46' transcriber <<EOF
UPDATE users SET Spent = Spent + $mins WHERE userID=$3;
UPDATE users SET Available = Allowed - Spent WHERE userID=$3;>>
EOF
echo "$min added to user $3"