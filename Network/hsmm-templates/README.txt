These files will replace the default files in the hsmm-pi folders on the RPi once they are setup.
If you wish to make changes to:
1. Files in hsmm-pi listed here:
  - change the file and once done, run the shell script found under MMNE/Network/Config/hsmm-copy.sh.
    Your changes will be put in the appropriate places in the hsmm-pi files.
  - WARNING: backup the orginal file before modifying
2. Other files in hsmm-pi NOT listed here:
  - Make a copy of the original file from hsmm-pi to this folder. Then change the shell script found
    under MMNE/Network/Config/hsmm-copy.sh wiht the following changes:
      sudo cp -f /home/pi/MMNE/Network/hsmm-templates/<FILENAME> /home/pi/hsmm-pi/<FILEPATH>/<FILENAME>
  - Make a backup of the original file (it's good practice)
    
