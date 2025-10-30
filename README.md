# Deployment
```bash
sudo -s
docker-compose up -d
#docker-compose up --build -d
```

# Installation
```bash
docker exec -it thesis bash
cd /root/thesis-codes/code/MyRouting/
ln -sf $PWD/xebel_offline.py /usr/local/bin/xebel-offline
ln -sf $PWD/xebel_online.py /usr/local/bin/xebel-online
ln -sf $PWD/xono-get.sh /usr/local/bin/xono-get
cd xebel_realtime/
make
ln -sf $PWD/xebel-realtime /usr/local/bin/xebel-realtime
ln -sf $PWD/xerclient.py /usr/local/bin/xerclient
```

# Usage
```bash
cd /root/configs/geant/config1
nano xebel.conf
xebel-offline --stage 1
xebel-offline --stage 2
#In another terminal:
cd /root/configs/geant/config1
xebel-online 

#In another terminal:
cd /root/configs/geant/config1
xebel-realtime

#In another terminal:
xono-get --help
xerclient "cmd..."
```
