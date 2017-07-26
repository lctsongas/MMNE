#!/bin/bash

if [ "$(id -u)" = "0" ]
  then echo "Please do not run as root, HTTP interface will not work"
  exit 1
fi

#install necessary extra files
sudo apt-get install hostapd


#Gets the eth0 MAC address and uses it for the 
#Access Point's (wlan1) IP address (192.168.xxx.1)
#Get MAC address 01:23:45:67:89:AB
mac=$(</sys/class/net/eth0/address)
#Get the last byte AB
lastbyte=$(echo $mac | cut -d':' -f 6)
#Convert byte to decimal AB = 171
decimal=$(echo $((16#$lastbyte)))
#Create IP address
addrIP="192.168.$decimal.1"
sudo ifconfig wlan1 down
sudo ifconfig wlan1 $addrIP netmask 255.255.$decimal.0
sudo ifconfig wlan1 up
templatePath="/home/pi/hsmm-pi/src/var/www/hsmm-pi/webroot/files/network_interfaces/interfaces.template"

#if sudo grep "allow-hotplug {wired_adapter_name}" $templatePath; then
#  echo "wlan1 already configured"
#else 
#  echo " " >> $templatePath
#  echo "allow-hotplug {wired_adapter_name}" >> $templatePath
#  echo "iface {wired_adapter_name} inet static" >> $templatePath
#  echo "    address $addrIP" >> $templatePath
#  echo "    netmask 255.255.255.0" >> $templatePath
#  echo "    network 192.168.$decimal.0" >> $templatePath
#fi

sudo service dhcpcd stop
sudo service hostapd stop
sudo service dnsmasq stop
sudo ifdown wlan1

#Save original DHCP server config and make new one for AP
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.original

#dhcpPath="/etc/dnsmasq.conf"
#echo "interface=wlan1" > $dhcpPath
#echo "dhcp-range=192.168.$decimal.20,192.168.$decimal.220,255.255.255.0,24h" >> $dhcpPath

#Setup hostapd.conf
hostapdPath="/etc/hostapd/hostapd.conf"
echo "interface=wlan1" > $hostapdPath
echo "driver=nl80211" >> $hostapdPath
echo "ssid=MMNE_AP" >> $hostapdPath
echo "hw_mode=g" >> $hostapdPath
echo "channel=7" >> $hostapdPath
echo "wmm_enabled=0" >> $hostapdPath
echo "macaddr_acl=0" >> $hostapdPath
echo "auth_algs=1" >> $hostapdPath
echo "ignore_broadcast_ssid=0" >> $hostapdPath
echo "wpa=2" >> $hostapdPath
echo "wpa_passphrase=Password1" >> $hostapdPath
echo "wpa_key_mgmt=WPA-PSK" >> $hostapdPath
echo "wpa_pairwise=TKIP" >> $hostapdPath
echo "rsn_pairwise=CCMP" >> $hostapdPath

sudo sed -i '/#DAEMON_CONF/c\DAEMON_CONF=/etc/hostapd/hostapd.conf' /etc/default/hostapd

#Setup hsmm-pi.conf

dnsConfPath="/home/pi/hsmm-pi/src/var/www/hsmm-pi/webroot/files/dnsmasq/hsmm-pi.conf.template"
#sudo sed -i "/dhcp-option=3,{lan_ip_address}/c\dhcp-option=3,$addrIP" $dnsConfPath

#sudo sed -i "s/{lan_dhcp_start}/192.168.$decimal.10/" $dnsConfPath

#sudo sed -i "s/{lan_dhcp_end}/192.168.$decimal.240/" $dnsConfPath

#sudo sed -i "s/{lan_netmask},24h/255.255.255.0,24h/" $dnsConfPath


#sudo sed -i "s/{lan_ip_address}/$addrIP/" $dnsConfPath

sudo ifup wlan1
sudo service dhcpcd start
sudo service hostapd start
sudo service dnsmasq start


exit 1
