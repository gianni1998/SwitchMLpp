# clear mininet and then start network.py

if [ -z "$1" ]; then
    mn -c && python -m python.network uhm
else
    mn -c && python -m python.network $1
fi