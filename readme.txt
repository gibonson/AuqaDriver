git rm -rf --cached .
git add .
git status


select avg(value) as srednia, count(value) as ilosc  FROM archive WHERE addInfo = 'Temperatura';
select deviceIP, deviceName ,type, addInfo  , count(value) as ilosc  FROM archive GROUP BY deviceIP, type, addInfo