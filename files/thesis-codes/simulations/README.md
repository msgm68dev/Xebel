Run in 3 terminals:

```bash
#1)
mininet.sh all
3

#2)
ryu-manager --observe-links ~/thesis-ryu/ryu/app/network_awareness/shortest_forwarding.py

#3)
python3 ~/thesis-ryu/ryu/app/network_awareness/external_app.py --kpaths 1 --weight hop
```
