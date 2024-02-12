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


ln /home/gibon/www/AuqaDriver/userFiles/config_email.ini /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/




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