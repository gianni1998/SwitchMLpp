# clear mininet and then start network.py

if [ -z "$1" ]; then
    mn -c && python network/network.py uhm
else
    mn -c && python network/network.py $1
fi