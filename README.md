# Auto-macOS-Installers
Automatically formats, partitions, and installs bootable macOS installers to a single USB drive

## How to use (macOS)
Before doing anything, please ensure you have the macOS installers downloaded and in the directory Applications/macOS Installers. 

Once you have the macOS installers in the correct location, plug in a USB and run the script. You will need to select your USB drive and the versions of macOS installers to put on it. From there, the script will create a partition and run the createinstallmedia commmand for each version.

## How to use (Linux)
If you are making a Linux drive, ensure the ISO you want to boot into is located in the "iso" folder in the same directory as the script.

Once you have downloaded a Linux ISO and moved it to the correct folder, plug in a USB and run the script. You will need to select the target USB and Linux ISO. After that, the script will automatically format and transfer the ISO to the flash drive.
