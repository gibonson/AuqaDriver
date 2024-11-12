# GIT:
git rm -rf --cached .
git add .
git status
gh repo clone gibonson/AuqaDriver
cd /home/gibon/www/AuqaDriver/AuqaDriver
git stash
gh repo sync
ln /home/gibon/www/AuqaDriver/userFiles/db.sqlite /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/
ln /home/gibon/www/AuqaDriver/userFiles/config_email.ini /home/gibon/www/AuqaDriver/AuqaDriver/userFiles/

# VIRTUAL ENV:
virtualenv venv/
source ./venv/bin/activate

# DOCKER:
sudo docker build . -t ptapp
sudo docker run -v $(pwd):/usr/src/app -d --restart=always --name aquadriver -p 5000:5000 ptapp 

# JSON EXAMPLE:

{
"addInfo": "BD creation",
"deviceName":"Server",
"deviceIP":"127.0.0.1",
"type":"Alert",
"value":10
}

# TO DO:
 - dodać API https://danepubliczne.imgw.pl/apiinfo

'''
graph TD
    subgraph WiFi_Network["Wi-Fi"]
        Hub[Hub]
        Sat1[Device 1 + 433MHz]
        Sat2[Device 2]
        Sat3[Device 3 + LoRa]
    
        Hub <-- HTTP --> Sat1
        Sat1 -- JSON --> Hub

        Hub <-- HTTP --> Sat2
        Sat2 -- JSON --> Hub

        Hub <-- HTTP --> Sat3
        Sat3 -- JSON --> Hub
    end

    subgraph LoRa_Devices["LoRa Devices"]
        direction LR
        LoRaSat1[Device 4 + LoRa]
        LoRaSat2[Device 5 + LoRa]
    end

    subgraph 433_Devices["433MHz Devices"]
        direction LR
        433Socket1[Device 4 + LoRa]
        433Socket2[Device 5 + LoRa]
    end

    Sat1 -- 433MHz --> 433Socket1
    Sat1 -- 433MHz --> 433Socket2

    Sat3 <-- LoRa --> LoRaSat1
    Sat3 <-- LoRa --> LoRaSat2

'''