git rm -rf --cached .
git add .
git status


select avg(value) as srednia, count(value) as ilosc  FROM archive WHERE addInfo = 'Temperatura';
select deviceIP, deviceName ,type, addInfo  , count(value) as ilosc  FROM archive GROUP BY deviceIP, type, addInfo



virtualenv venv/
source ./venv/bin/activate

gh repo clone gibonson/AuqaDriver


git stash
gh repo sync
ln  /home/gibon/www/AuqaDriver/userFiles/db.sqlite /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/db.sqlite



