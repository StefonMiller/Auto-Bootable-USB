# Auto-Bootable-USB
Automatically formats, partitions, and installs bootable macOS/Linux installers for a given USB

## Making Windows Installers (Windows Only)
**You must run this script as an administrator**

Please first download a Windows ISO and place it in the "Windows" folder alongside the script. 

Once you have the Windows ISO in the right place, you can simply run the script and it will take care of the rest!

## Making macOS Installers (macOS Only)
Before doing anything, please ensure you have the macOS installers downloaded and in the directory Applications/macOS Installers. 

Once you have the macOS installers in the correct location, plug in a USB and run the script. You will need to select your USB drive and the versions of macOS installers to put on it. From there, the script will create a partition and run the createinstallmedia commmand for each version.

## Making Linux Installers (Windows/macOS)
If you are making a Linux drive, ensure the ISO you want to boot into is located in the "iso" folder in the same directory as the script.

Once you have downloaded a Linux ISO and moved it to the correct folder, plug in a USB and run the script. You will need to select the target USB and Linux ISO. After that, the script will automatically format and transfer the ISO to the flash drive.
