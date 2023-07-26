#!/bin/bash
mysql -u bots --password='editor46' transcriber <<EOF
CREATE TABLE users (
  userID INT,
  Firstname VARCHAR(255),
  Username VARCHAR(255),
  Name VARCHAR(255),
  Telephone VARCHAR(255),
  Sum INT,
  Allowed INT,
  Spent INT,
  Available INT,
  Date VARCHAR(255),
  Level INT
);
LOAD DATA INFILE '/var/lib/mysql-files/user.csv' INTO TABLE users FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1
LINES SET Firstname = NULLIF(Firstname, ''), Username = NULLIF(Username, ''), Telephone = NULLIF(Telephone, ''), Name = NULLIF(Name, '');
ALTER TABLE users ADD COLUMN FormattedDate DATE;
UPDATE users SET FormattedDate = STR_TO_DATE(Date, '%d.%m.%Y %H:%i:%s');
EOF
