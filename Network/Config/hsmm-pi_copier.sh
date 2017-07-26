#!/bin/bash
#Add filename of hsmm-pi file you want to modify with your own file
#Make sure the modified file matchesd the original filename AND
#you add the file to the MMNE/
MMNE_files=("AppController.php" 
            "NetworkSettingsController.php"
            "interfaces.template"
            "olsrd.conf.template"
            "hsmm-pi.conf.template")

HSMM_HOME='/home/pi/hsmm-pi'
MMNE_HOME='/home/pi/MMNE'
for file in ${MMNE_files[@]}; do   # The quotes are necessary here
  echo "replacing: $file"
  path_str=$(find "$HSMM_HOME" -name $file)
  IFS=$' ' read -rd '' -a path_list <<< $path_str
  path=${path_list[0]}
  path="${path%$'\n'}"
  if ! [ -f "$path-original" ]; then
    echo "Making backup of: $file"
    cp -f $path "$path-original"
  fi
  cp -f "$MMNE_HOME/Network/hsmm-templates/$file" $path
  echo "Modified $file added to hsmm-pi"
done
echo "Please connect to: 127.0.0.1:8080 in web browser"
echo "login and go to admin->network then click save"
echo "reboot device to apply changes"

exit 0
