#!/bin/bash
#This will intall all necessary packages for the MMNE project

if [ "$(id -u)" = "0" ]
  then echo "Please do not run as root, HTTP interface will not work"
  exit 1
fi

PKG_HOME="$HOME"

#hsmm-pi installation block
cd "$PKG_HOME/Downloads"
sudo git clone https://github.com/urlgrey/hsmm-pi.git
cd hsmm-pi
sh ./install.sh
hsmmOK=$?; 
if [[ $hsmmOK != 0 ]]; then 
  echo "[install_pkg] hsmm-pi failed to install"
  exit $hsmmOK; 
fi
echo "[install_pkg] hsmm-pi installed successfully"

#Copy MMNE modified config files to hsmm-pi
cd $PKG_HOME/MMNE/Network/Config
sudo sh ./copyMMNEtoHSMM
copyOK=$?; 
if [[ $copyOK != 0 ]]; then 
  echo "[install_pkg] copying failed"
  exit $copyOK; 
fi
echo "[install_pkg] network config files copied successfully"
