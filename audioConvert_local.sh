#!/bin/bash
echo "input $1 output $2 user_ID $3"
date
var=$(ffmpeg -i "$1" -acodec libmp3lame "$2" 2>&1 | grep Duration)
echo "$2 $var">> duration.txt
mins=$(echo $var | awk -F: '{print $2*60+$3}') #getting minutes
echo "Total minutes: $mins"
mysql --defaults-file=~/.bots.cnf <<EOF
UPDATE users SET Spent = Spent + $mins WHERE userID=$3;
UPDATE users SET Available = Allowed - Spent WHERE userID=$3;
#UPDATE users SET Level = 1 WHERE userID=$3 AND Allowed * 0.9 < Spent;
UPDATE users SET Level = 1 WHERE userID=$3 AND Available < 30;
UPDATE users SET Level = 0 WHERE userID=$3 AND  Available < 10;
EOF
echo "$min added to user $3"

####
#mysql> UPDATE users SET Level = 0 WHERE userID='959676595' AND Available > Allowed; #change to level 0 if there is no mins left
#Query OK, 0 rows affected (0.00 sec)
#Rows matched: 0  Changed: 0  Warnings: 0
#
#mysql> UPDATE users SET Level = 0 WHERE userID='959676595' AND Available > Allowed * 0.9; #change to level 0 if there is no mins left
#Query OK, 1 row affected (0.01 sec)
#Rows matched: 1  Changed: 1  Warnings: 0
####