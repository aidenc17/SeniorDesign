## PC to AWS Script (Windows OS /w python)

### This script is designed to upload images form any local Windows OS PC to aws with minimal setup required
 #### Files added:
```
            - auto_sftp_forwarder.exe
            - auto_sftp_forwarder.py
```
### Instructions on how to setup this files.
 1. upload the `Incoming` Folder from USB to the local laptop / PC.
 2. If OS `windows` double click on the exe file.
 3. the `.exe` file will open a terminal and wait for any files that have video / image extensions assigned by the script inside the folder.
    Note: this script requires PEM key to communicate to AWS servers, so it needs to be added same directory as the script / `.exe` file.
 4. The `.exe` and the script is configured to SKIP configuration files and PEM keys and can be changed in the script.
 5. If you want files added and uploaded to AWS it needs to be inside `Incoming` folder.
 6. It will be uploaded to the `Private` folder in the AWS where nginx will pull its data from Authenticated Users.

Note to self or any other user who will use thsi script, Don't forget to turn on AWS.
