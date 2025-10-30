echo DEPRECATED! USE myrouting.sh INSTEAD
echo
printf "If not stopped, it will start after 5 seconds: "
for i in 1 2 3 4 5
do
 sleep 1
 printf "$i, "
done
~/thesis-ryu/mostafa/talk_to_ryu.py
