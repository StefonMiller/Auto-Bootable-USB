"""
	Please feel free to edit this to your heart's content!

	with love
	- Kevin C
	- Stefon M
"""
import os
from sys import stderr, stdout, stdin
import subprocess
import glob
from subprocess import Popen, PIPE
from threading import Thread
from sys import platform
import time

# TODO Figure out how to disable buffereing with subprocess in order to have the live progress bars with os.system/popen

# Class encapsulating data on macOS versions
class Version:
	# Initialize class objects with data
	# @Param name: Version name 
	# @Param size: Version size
	# @Param command: createinstallmedia command to install the version
	def __init__(self, name, size, command):
		self.name = name
		self.size = size
		self.command = command

# Class encapsulating data on each external disk
class Disk:
	# Initialize class objects with data
	# @Param label: Disk label
	def __init__(self, label, size):
		self.label = label
		self.size = size

# Function threads will target to execute install commands simultaneously
# @Param command: Command to execute
def runInstallCommand(command):
	os.system(command)

# Displays all external devices to user and prompts for them to select one
# @Return: The label, name, and size of the selected disk
def get_disk():
	# Prompt for the user to select a disk
	output_str = "Please select the flash drive to write installers to:\n"
	# Execute the diskutil list command and store the output in a variable
	command = "diskutil list"
	# Split the output by line for iteration
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = proc.communicate()
	lines = out.decode().split('\n')
	disks = []
	# Iterate through each line
	for line in lines:
		# If a line contains /dev/disk then it signifies a new disk in the output. 
		# We only evaluate disks that are external to omit internal hard drives/busses
		if(("/dev/disk" in line) and ("external" in line)):
			# Add a new Disk object to the array of disks
			disks.append(Disk(line.split(" ")[0]))

	# Iterate through the disks and get information on their names and sizes 
	for disk in disks:
		# Run the diskutil info command and store the output in a variable for each disk
		command = "diskutil info " + disk.label
		# Split the output by line and iterate through them
		disk_info = os.popen(command).read().split('\n')
		for info in disk_info:
			# Locate the device name and size and store the results in a variable
			if("Device / Media Name" in info):
				# Split the name by spaces and then cut off the first 13 elements of the array to get the actual name
				# Then join the remaining words together
				disk.name = " ".join(info.split(" ")[13:])
			if("Disk Size" in info):
				# Split the size by spaces and then cut off the first 21 and last 6 entries. Join the remaining 
				# values together
				disk.size = float(" ".join(info.split(" ")[21:-6]))


	num_disks = 1
	# Display all external disk names
	for disk in disks:
		output_str += ("\t" + str(num_disks) + "). " + disk.name + '\n')
		num_disks += 1

	disk_choice = 999
	# Loop until we receive a valid input
	while(disk_choice > num_disks or disk_choice < 1):
		disk_choice = int(input(output_str))
	
	# Return the selected disk information
	return disks[disk_choice-1].label, disks[disk_choice-1].name, disks[disk_choice-1].size

# Formats a specified disk
# @Param disk_label: Label of selected disk
# @Param disk_name: Name of selected disk
# @Param format: Format of disk
# @Param partition_scheme: Partition scheme of disk
def format_disk(disk_label, disk_name, format, partition_scheme):
	to_format = ""
	# Ensure the user wants to format the disk
	while(to_format != 'n' and to_format != 'y'):
		to_format = input("\n\nAre you sure you want to format " + disk_name + "? (y/n)\n")

	# If the user confirms, format the disk
	if(to_format == 'y'):
		# Replace spaces in the name with "\ " to support multi-word disk names
		disk_name = disk_name.replace(" ", "\ ")
		# If we are trying to create a linux drive, set the name to a FAT32-compliant one
		if(format == "exFAT"):
			disk_name = "LINUX"
		# Format disks to the specified format
		command = "diskutil eraseDisk " + format + " \"" + disk_name + "\" " +  partition_scheme + " " + disk_label
		os.system(command)
	else:
		exit(0)

# Displays a list of all supported versions and returns a list of all ones selected by the user
# @Param name: Name of disk to install versions to
# @Param size: Size of disk to install versions to
# @Param versions: Dict of selected versions
# @Return an array of all versions selected by the user
def select_versions(name, size, versions):
	# Display name and size of drive 
	print("\n\nDisk " + name + " has " + str(size) + " GB free")
	print("Please select the OS's you would like to install on the disk. Enter -2 to clear and -1 to confirm selection:")
	selection = []
	i = 1
	# Loop through all supported versions and display their associated names and sizes
	for version in versions.values():
		print("\t" + str(i) + ". " +  version.name + " (" + str(version.size) + "GB)")
		i += 1
	
	entry = 0
	curr_size = 0
	# Prompt the user to select versions until they enter -1
	while(entry != -1):
		# Display all versions we are going to install upon every iteration
		entry = int(input("Currently installing: " + str(selection) + "\n"))
		# Ensure the user input is a valid selection
		if(entry > 0 and entry <= len(versions.values())):
			# Get the version the user selected
			temp = list(versions.values())[entry-1]
			# Ensure there is enough space on the drive for the selected version
			# and it has not already been selected
			if(((curr_size + temp.size) < size) and (temp.name not in selection)):
				# If the selection is valid, add it to the list an update the current install size
				selection.append(temp.name)
				curr_size += temp.size
			# Inform the user if the drive needs more space
			elif((curr_size + temp.size) >= size):
				print("Need " + str((curr_size + temp.size) - size) + " more GB to add " + temp.name)
		# If the user entered -2, clear the array and set the size to 0
		elif(entry == -2):
			selection = []
			curr_size = 0
	
	# Return an array of all OS versions selected by the user
	return selection
	

# Partitions a selected drive with n partitions where n is the number of OS's selected by them
# @Param selected_versions: List of versions selected by the user
# @Param version_list: Dict of all versions and their respective version objects
# @Param disk_label: Label of disk to partition
def partition_drive(selected_versions, version_list, disk_label):
	command = "diskutil partitionDisk " + disk_label + " GPT " 
	# For each selected version, create a partition that is large enough to house it
	for version in selected_versions:
		command += "JHFS+ Install\ macOS\ " + version.replace(" ", "\ ") + " " + str(version_list[version].size) + "g "

	os.system(command)

# Forcibly ejects and mounts the drive to cut ties to any processes using it
def free_disk(label, password):
	command = "diskutil unmountDisk force " + label
	os.system(command)
	command = "echo " + password + " | sudo -S diskutil mountDisk " + label
	os.system(command)

# Lists all ISO files in the current directory and prompts the user to select one
# @Return: Path to selected iso
def select_iso():
	files = []
	os.chdir("iso")
	# Add any files with the iso extension to a list
	for file in glob.glob("*.iso"):
		files.append(file)
	
	# Inform user if no isos found
	if not files:
		print("No ISO files found. Please make sure the ISO is in a folder named \"iso\" in the same directory as this script")
		exit(0)
	else:
		# If there are ISOs, have the user select one
		output_str = ("\nPlease select an ISO to use:\n")
		i = 1
		for file in files:
			output_str += ("\t" + str(i) + "). " + file + "\n")

		iso = 999
		# Loop until we receive a valid input
		while(iso > i or iso < 1):
			iso = int(input(output_str))

		# Return path to iso file
		return os.path.abspath(files[i-1])
		
# Converts a given iso to an img file
# @Param iso: path to ISO file
# @Return: Path to img file
def convert_to_img(iso):
	# Get the name of the iso
	img_name = ".".join(iso.split("/")[-1].split(".")[:-1])
	# Replace the name iso directory with dmg and add the iso name
	img_path = "/".join(iso.split("/")[:-1]).replace("iso", "img") + "/" + img_name

	os.chdir("../img")
	# Check if the file name already exists
	for file in glob.glob("*.img"):
		if(file == (img_name + ".img")):
			# If the file name already exists, ask the user if they'd like to replace it
			replace = ""
			while replace != "y" and replace != "n":
				replace = input("A disk image for this iso already exists. Would you like to replace it? (y/n)\n").lower()
			# If they want to replace the dmg, remove the file and execute the command. Otherwise just return
			if replace == "y":
				command = "rm " + img_path
				os.system(command)
			else:
				return img_path
	# Use hdiutil to convert the iso to dmg and return the path to it
	command = "hdiutil convert -format UDRW -o " + img_path + ".img " + iso
	os.system(command)
	command = "mv " + img_path + ".img.dmg" + " " + img_path + ".img"
	os.system(command)
	return img_path

# Transfers items from a disk image to a USB
# @Param img: Path to dmg file
# @Param label: Label of disk to transfer to
def transfer_to_disk(img, label):
	label = label.split("/")
	label[-1] = "r" + label[-1]
	label = "/".join(label)
	# Unmount disk before executing command to avoid the "Resource Busy" error
	command = "sudo diskutil unmountDisk " + label
	os.system(command)
	# Transfer img file to usb
	print("\nStarting transfer...")
	command = "sudo dd if=" + img + ".img of=" + label + " bs=1m"
	os.system(command)
	# Eject drive once finished
	command = "diskutil eject " + label
	os.system(command)


# Creates a bootable macOS drive with support for multiple partitions
# @Param password: Password for the computer
def create_macos_drive(self, password):
	threads = []
	# Get the label, name, and capacity of the disk the user wants to use
	disk_label, disk_name, disk_size = self.get_disk()
	# Force eject and mount the disk before attempting to format it
	self.free_disk(disk_label, password)

	# Format the selected disk
	self.format_disk(disk_label, disk_name, "JHFS+", "")

	# Define the locations of the installer files and the createinstallmedia script
	installer_loc = r'/Applications/macOS\ Installers'
	script_loc = '.app/Contents/Resources/createinstallmedia'

	# Dictionary of versions and their associated version objects
	versions = {
		"Big Sur": Version("Big Sur", 14, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Big\ Sur' + script_loc + ' --volume /Volumes/Install\ macOS\ Big\ Sur --nointeraction')),
		"Catalina": Version("Catalina", 10, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Catalina' + script_loc + ' --volume /Volumes/Install\ macOS\ Catalina --nointeraction')),
		"Mojave": Version("Mojave", 7, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Mojave' + script_loc + ' --volume /Volumes/Install\ macOS\ Mojave --nointeraction')),
		"High Sierra": Version("High Sierra", 7, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ High\ Sierra' + script_loc + ' --volume /Volumes/Install\ macOS\ High\ Sierra --nointeraction'))
	}

	# Get the versions the user would like to install
	selected_versions = self.select_versions(disk_name, disk_size, versions)
	# Partition the drives according to the selected versions
	self.partition_drive(selected_versions, versions, disk_label)


	# Loop through the selected versions and execute the install commands associated with them
	for version in selected_versions:
		volume_path = "/Volumes/Install\ macOS\ " + version.replace(" ", "\ ") 
		command = versions[version].command
		thread = Thread(target=self.runInstallCommand, args=(command,))
		threads.append(thread)
		thread.start()

	# Once we have threads associated with each OS install, attempt to execute the commands simultaneously
	for index, thread in enumerate(threads):
		thread.join()

def create_linux_drive(self, password):
	threads = []
	# Get the label, name, and capacity of the disk the user wants to use
	disk_label, disk_name, disk_size = self.get_disk()
	# Force eject and mount the disk before attempting to format it
	self.free_disk(disk_label, password)

	# Format the selected disk
	self.format_disk(disk_label, disk_name, "exFAT", "GPT")

	# Have user select the ISO to install
	iso = self.select_iso()

	# Convert the ISO file to an .img file
	img = self.convert_to_img(iso)

	# Transfer the .img file to the USB
	self.transfer_to_disk(img, disk_label)
	print("Transfer complete. USB is ready for use")


def create_windows_drive():
	# Path to Windows install iso
	iso_path = os.path.abspath("iso/Windows.iso").replace("\\", "\\\\")
	# Display all disks to the user and have them select one to format
	disk_num = select_disk()
	# Format the disk using diskpart
	disk_label = format_disk_windows(disk_num)
	
	iso_label = get_label()
	# If the W10 iso isn't already mounted, mount it with powershell
	if iso_label is None:
		command = "Powershell Mount-DiskImage -ImagePath " + iso_path
		p = Popen(command, shell=True)
		p.communicate()
		iso_label = get_label()
	
	# Copy the iso to the drive
	start_copy(iso_label, disk_label)

	# After the copy, unmount the iso
	command = "Powershell Dismount-DiskImage -ImagePath " + iso_path
	p = Popen(command, shell=True)
	p.communicate()

	print("Windows ISO is ready for use")

# Displays all mounted disks and prompts the user to select one
# @Return: Number of selected disk
def select_disk():
	# Open diskpart and execute the list disk command
	p = Popen("diskpart", shell=True, stdin=PIPE, stdout=PIPE)
	time.sleep(.5)
	p.stdin.write(bytes("list disk\n", 'utf-8'))
	# Store output of list disk in a variable
	out, err = p.communicate()
	out = out.decode().split("\n")

	disks = []

	# Parse the output of diskpart into a Disk object
	output = "Please select one of the following disk numbers:\n"
	for line in out:
		if("Online" in line):
			line = line.split(" ")
			# Parse the output of diskpart and store the disk name and size in a Disk object
			disk_name = line[2] + " " + line[3]
			# Disks need to have at least 1GB capacity to be candidates
			disk_size = line[line.index("GB") - 1]
			output += "\t" + disk_name + ":\t" + disk_size + " GB\n"
			disks.append(Disk(disk_name, disk_size))
	# Prompt the user to select one of the disks from diskpart
	disk = -1
	while(not (-1 < disk < len(disks))):
		# Drives need at least 12GB of space to be candidates
		if(int(disks[disk].size) < 12):
			print("Not enough space on this drive for Windows")
			disk = -1
		else:
			disk = int(input(output))
	# Return disk selection
	return disk

# Formats a disk using a diskpart script
# @Param disk_num: Disk number selected by the user
# @Return: The label of the formatted disk
def format_disk_windows(disk_num):
	# Write commands to format and partition the disk to a txt file
	with open("commands.txt", "wt") as file:
		file.write("select disk " + str(disk_num) + "\n")
		file.write("clean\n")
		file.write("convert mbr\n")
		file.write("create partition primary\n")
		file.write("select partition 1\n")
		file.write("active\n")
		file.write("format FS=NTFS quick\n")
		file.write("assign letter=X\n")
		file.write("exit")
	# Get path to file 
	file_path = os.path.realpath(file.name)
	file.close()

	# Replace \ characters in file with \\
	file_path = file_path.replace("\\", "\\\\")
	# Open a diskpart process with the script flag to execute the command text file created
	command = "diskpart /s " + file_path
	p = Popen(command, shell=True, stdin=PIPE, stderr=PIPE)
	p.communicate()

	return "X"

# Uses diskpart to get the label of the W10 iso
# @Return: None if the W10 iso isn't mounted. The label of the iso if it is mounted
def get_label():
	# Open diskpart and execute the list disk command
	p = Popen("diskpart", shell=True, stdin=PIPE, stdout=PIPE)
	time.sleep(.5)
	p.stdin.write(bytes("list volume\n", 'utf-8'))
	# Store output of list disk in a variable
	out, err = p.communicate()
	out = out.decode().split("\n")
	
	label = None
	# If the W10 iso is mounted, return the label of it
	for line in out:
		if(("ESD-ISO" in line) and ("DVD-ROM" in line)):
			line = line.split(" ")
			label = line[8]
	
	return label

# Initializes the copy process from the W10 iso to the target USB
# @Param iso: Label of the ISO
# @Param disk: Label of the disk
def start_copy(iso, disk):
	if(iso is None):
		print("No iso found. Please make sure there is a valid Windows ISO in the \"iso\" directory")
		exit(0)
	# Navigate to the iso's boot directory and set the bootsect to /nt60. Then copy the files from the iso to the disk
	command = iso + ": && cd boot && bootsect /nt60 " + disk + ": && " + "xcopy " + iso + ":\*.* "  + disk + ":\ /E /F /H"
	p = Popen(command, shell=True)
	p.communicate()
		

if __name__ == "__main__":
	while(True):
		drive_type = 0
		if platform == "linux" or platform == "linux2" or platform == "darwin":
			drive_type = int(input("Would you like to create a macOS or linux drive?\n\t1). macOS\n\t2). Linux\n\t"))

		if(drive_type == 1):
			os.system("stty -echo")
			password = input("What is the password for this account?")
			os.system("stty echo")
			print("\n")
			create_macos_drive(password)
			exit(0)
		elif(drive_type == 2):
			os.system("stty -echo")
			password = input("What is the password for this account?")
			os.system("stty echo")
			print("\n")
			create_linux_drive(password)
			exit(0)
		elif(platform == "win32"):
			print("Detected Windows computer. Creating a Windows installer...")
			create_windows_drive()
			exit(0)
		else:
			print("Please select a valid option")
		
