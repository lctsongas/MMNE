#!/bin/bash
#This will intall all necessary packages for the MMNE project

if [ "$(id -u)" != "0" ]
  then echo "Please run as root,"
  exit 1
fi

ask() {
  # https://djm.me/ask
  local prompt default REPLY

  while true; do

    if [ "${2:-}" = "Y" ]; then
      prompt="Y/n"
      default=Y
    elif [ "${2:-}" = "N" ]; then
      prompt="y/N"
      default=N
    else
      prompt="y/n"
      default=
    fi
      # Ask the question (not using "read -p" as it uses stderr not stdout)
      echo -n "$1 [$prompt] "

      # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
      read REPLY </dev/tty

      # Default?
      if [ -z "$REPLY" ]; then
        REPLY=$default
      fi

      # Check if the reply is valid
      case "$REPLY" in
        Y*|y*) return 0 ;;
        N*|n*) return 1 ;;
      esac

  done
}

PKG_HOME="/home/pi"
GIT_HOME="/home/pi/Downloads/github"
mkdir $GIT_HOME
echo "Make sure you have internet connection before running!"
echo "This step will take a long time. But is highly recommended"
echo "if you are running this on a fresh RPi install"
if ask "Update and upgrade RPi?" ; then
  echo "Updating libraries and stuff... This will take awhile"
  sleep 2
  sudo apt-get update
  sudo apt-get upgrade
  sudo apt-get install -y linux-headers-4.9.0-2-all build-essential dkms
  sudo ln -s /lib/modules/4.9.0-2-rpi/* /lib/modules/4.9.35-v7+/
fi

sudo apt-get install -y git

echo "Installing github dependencies:"
cd $GIT_HOME

echo "[GIT] IMU Sensor"
IMU_Path="$GIT_HOME/IMU"
mkdir $IMU_Path
if ! [ $? -eq 0 ]; then
  echo "IMU repo already exists!"
else
  cd $IMU_Path
  IMU_Cmd="git clone https://github.com/adafruit/Adafruit_Python_BNO055.git"
  echo "[GIT] $IMU_Cmd"
  eval $IMU_Cmd
  cd "$IMU_Path/Adafruit_Python_BNO055"
  sudo python setup.py install
fi
echo "[GIT] IMU Sensor Done!"

echo "[GIT] ADC Sensor"
ADC_Path="$GIT_HOME/ADC"
mkdir $ADC_Path
if ! [ $? -eq 0 ]; then
  echo "ADC repo already exists!"
else
  cd $ADC_Path
  ADC_Cmd="git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git"
  echo "[GIT] $ADC_Cmd"
  eval $ADC_Cmd
  cd "$ADC_Path/Adafruit_Python_ADS1x15"
  sudo python setup.py install
fi
echo "[GIT] ADC Sensor Done!"

echo "[GIT] Motor HAT"
MHAT_Path="$GIT_HOME/Motor_HAT"
mkdir $MHAT_Path
if ! [ $? -eq 0 ]; then
  echo "Motor HAT repo already exists!"
else
  cd $MHAT_Path
  MHAT_Cmd="git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git"
  echo "[GIT] $MHAT_Cmd"
  eval $MHAT_Cmd
  cd "$MHAT_Path/Adafruit-Motor-HAT-Python-Library"
  sudo python setup.py install
fi
echo "[GIT] Motor HAT Done!"

echo "[GIT] HSMM-Pi"
HSMM_Path="$GIT_HOME/HSMM-Pi"
mkdir $HSMM_Path
if ! [ $? -eq 0 ]; then
  echo "HSMM-Pi repo already exists!"
else
  cd $HSMM_Path
  HSMM_Cmd="git clone https://github.com/urlgrey/hsmm-pi.git"
  echo "[GIT] $HSMM_Cmd"
  eval $HSMM_Cmd
  cd "$HSMM_Path/hsmm-pi"
  sudo runuser -l pi -c "$HSMM_Path/hsmm-pi/install.sh"
fi
echo "[GIT] HSMM-Pi Done!"

echo "[GIT] AP (rtl8192cu) Driver"
AP_Path="$GIT_HOME/AP"
mkdir $AP_Path
if ! [ $? -eq 0 ]; then
  echo "AP repo already exists!"
else
  cd $AP_Path
  AP_Cmd="git clone https://github.com/pvaret/rtl8192cu-fixes.git"
  echo "[GIT] $AP_Cmd"
  eval $AP_Cmd
  cd "$AP_Path/AP"
  sudo dkms add .
  sudo dkms install 8192cu/1.10
  sudo depmod -a
fi
echo "[GIT] HSMM-Pi Done!"

#All git files downloaded successfully

echo "[GET] GPS"
sudo apt-get install -y gpsd gpsd-clients python-gps
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
echo "[GET] GPS Done!"

echo "[GET] Hostapd"
sudo apt-get install -y hostapd
echo "[GET] Hostapd done!"


#Begin setting up UART and stopping bluetooth
echo "[BOOT] Modifying boot files"
bootcfg="/boot/config.txt"
echo "enable_uart=1" >> $bootcfg
echo "dtoverlay=pi3-miniuart-bt" >> $bootcfg
sudo systemctl stop serial-getty@ttyS0.service
sudo systemctl disable serial-getty@ttyS0.service
bootcmd=$(cat /boot/cmdline.txt)
echo "${go#[^\s]*serial0[^\s]*}" > $bootcmd
echo "[BOOT] boot files Done!"

#Begin setting up network now
echo "[NET] Setting up Network"
NETCFG_PATH="$PKG_HOME/MMNE/Network/Config"
/bin/bash "$NETCFG_PATH/hsmm-pi_copier.sh"
/bin/bash "$NETCFG_PATH/create_AP_IP.sh"

sudo cp "$NETCFG_PATH/hostapd.conf" "/etc/hostapd/"
sudo mv "/usr/sbin/hostapd" "/usr/sbin/hostapd.bak"
sudo cp "$NETCFG_PATH/hostapd" "/usr/sbin/"
sudo chown root /usr/sbin/hostapd
sudo chmod 775 /usr/sbin/hostapd

sudo cp "$NETCFG_PATH/dhcpcd.conf" "/etc/dhcpcd.conf"

echo "[NET] Network Setup Done!"

echo "Reboot the RPi for changes to take effect"



