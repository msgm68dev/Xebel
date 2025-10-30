if (( $(ps aux | grep ryu-manager | wc -l ) > 1 ))
then

	~/thesis-codes/code/MyRouting/MyRouting.py
else
	echo "Start ryu.sh first!"
	~/thesis-codes/code/MyRouting/MyRouting.py
	exit 1
fi
