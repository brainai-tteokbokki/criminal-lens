# Check if the script is running as root(service).
if [ $(id -u) -ne 0 ]; then
    echo "setup.sh must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

# install
sudo apt update
sudo apt install libgl1-mesa-glx
sudo pip install -r requirements.txt