# DIAGRAM

```mermaid
graph TD
    subgraph WiFi_Network["Home Wi-Fi"]
        subgraph Hub[Aqua Driver Hub]
            DB[(Archive)]
        end
        Sat1[ESP8266 + 433MHz]
        Sat2[ESP8266 + Sensors]
        Sat3[ESP8266 + LoRa]


        Hub <-- HTTP --> Sat1
        Sat1 -- JSON --> Hub

        Hub <-- HTTP --> Sat2
        Sat2 -- JSON --> Hub

        Hub <-- HTTP --> Sat3
        Sat3 -- JSON --> Hub
    end

    subgraph LoRa_Devices["LoRa"]
        LoRaSat1[Arduino + LoRa]
        LoRaSat2[Arduino + LoRa]
    end

    subgraph 433_Devices["433MHz"]
        433Socket1[Socket]
        433Socket2[Socket]
    end

    Sat1 -- 433MHz --> 433Socket1
    Sat1 -- 433MHz --> 433Socket2

    Sat3 <-- LoRa --> LoRaSat1
    Sat3 <-- LoRa --> LoRaSat2
```

# Configuration

## GIT:
- git rm -rf --cached .
- git add .
- git status
- gh repo clone gibonson/AuqaDriver
- cd /home/gibon/www/AuqaDriver/AuqaDriver
- git stash
- gh repo sync
- ln /home/gibon/www/AuqaDriver/userFiles/db.sqlite /home/gibon/www/AuqaDriver/AuqaDriver/- userFiles/
- ln /home/gibon/www/AuqaDriver/userFiles/config_email.ini /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/

## VIRTUAL ENV:
- virtualenv venv/
- source ./venv/bin/activate

## DOCKER:
- sudo docker build . -t ptapp
- sudo docker run -v $(pwd):/usr/src/app -d --restart=always --name aquadriver -p 5000:5000 ptapp 

## JSON EXAMPLE:

{
"addInfo": "BD creation",
"deviceName":"Server",
"deviceIP":"127.0.0.1",
"type":"Alert",
"value":10
}

## TO DO:
 - add API https://danepubliczne.imgw.pl/apiinfo