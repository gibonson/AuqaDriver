git rm -rf --cached .
git add .
git status


select avg(value) as srednia, count(value) as ilosc  FROM archive WHERE addInfo = 'Temperatura';
select deviceIP, deviceName ,type, addInfo  , count(value) as ilosc  FROM archive GROUP BY deviceIP, type, addInfo



virtualenv venv/
source ./venv/bin/activate

gh repo clone gibonson/AuqaDriver

cd /home/gibon/www/AuqaDriver/AuqaDriver
git stash
gh repo sync
ln  /home/gibon/www/AuqaDriver/userFiles/db.sqlite /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/
ln /home/gibon/www/AuqaDriver/userFiles/config_email.ini /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/

sudo docker build . -t ptapp

sudo docker run -v $(pwd):/usr/src/app -d --restart=always --name aquadriver -p 5000:5000 ptapp 




select *  FROM archive WHERE timestamp > 1707759123 AND deviceName = "Server" GROUP BY deviceIP, type, addInfo;


--         print(form.title.data)
--         print(form.description.data)
--         print(form.deviceIP.data)
--         print(form.deviceName.data)
--         print(form.addInfo.data)
--         print(form.type.data)
--         print(form.avgOrSum.data)
--         print(form.timerRangeHours.data)
--         print(form.quantityValues.data)
--         print(form.minValue.data)
--         print(form.okMinValue.data)
--         print(form.okMaxValue.data)
--         print(form.maxValue.data) 