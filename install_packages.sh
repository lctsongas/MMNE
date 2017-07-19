#!/bin/bash
#This will intall all necessary packages for the MMNE project

if [ "$(id -u)" != "0" ]
  then echo "Please run as root, HTTP interface will not work"
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
  git clone https://github.com/adafruit/Adafruit_Python_BNO055.git
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
  git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git
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
  git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git
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
  git clone https://github.com/urlgrey/hsmm-pi.git
  cd "$HSMM_Path/hsmm-pi"
  sh install.sh
fi
echo "[GIT] HSMM-Pi Done!"


#hsmm-pi installation block
#mkdir "$
#cd "$PKG_HOME/Downloads"
#sudo git clone https://github.com/urlgrey/hsmm-pi.git
#cd hsmm-pi
#sh ./install.sh
#hsmmOK=$?; 
#if [[ $hsmmOK != 0 ]]; then 
#  echo "[install_pkg] hsmm-pi failed to install"
#  exit $hsmmOK; 
#fi
#echo "[install_pkg] hsmm-pi installed successfully"
#
##Copy MMNE modified config files to hsmm-pi
#cd $PKG_HOME/MMNE/Network/Config
#sudo sh ./copyMMNEtoHSMM
#copyOK=$?; 
#if [[ $copyOK != 0 ]]; then 
#  echo "[install_pkg] copying failed"
#  exit $copyOK; 
#fi
#echo "[install_pkg] network config files copied successfully"

