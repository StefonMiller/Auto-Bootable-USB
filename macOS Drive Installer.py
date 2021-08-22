"""
	Please feel free to edit this to your heart's content!

	with love
	- Kevin C
	- Stefon M
"""
import os
from sys import stderr, stdout, stdin
import subprocess, re
import glob
import shutil
from threading import Thread

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
	def __init__(self, label):
		self.label = label
		self.name = ""
		self.size = ""

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
		output_str += (str(num_disks) + ":\t " + disk.name + '\n')
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
def format_disk(disk_label, disk_name):
	to_format = ""
	# Ensure the user wants to format the disk
	while(to_format != 'n' and to_format != 'y'):
		to_format = input("\n\nAre you sure you want to format " + disk_name + "? (y/n)\n")

	# If the user confirms, format the disk
	if(to_format == 'y'):
		# Replace spaces in the name with "\ " to support multi-word disk names
		disk_name = disk_name.replace(" ", "\ ")
		# Format disks to JHFS(macOS extended journaled)
		command = "diskutil eraseDisk JHFS+ " + disk_name + " " + disk_label
		os.system(command)
	else:
		exit(0)

# Displays a list of all supported versions and returns a list of all ones selected by the user
# @Param name: Name of disk to install versions to
# @Param size: Size of disk to install versions to
# @Return an array of all versions selected by the user
def select_versions(name, size):
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

threads = []

password = input("What is the password for this account?")

# Get the label, name, and capacity of the disk the user wants to use
disk_label, disk_name, disk_size = get_disk()
# Format the selected disk
format_disk(disk_label, disk_name)

# Define the locations of the installer files and the createinstallmedia script
installer_loc = r'/Applications/macOS\ Installers'
script_loc = '.app/Contents/Resources/createinstallmedia'

# Dictionary of versions and their associated version objects
versions = {
	"Big Sur": Version("Big Sur", 13, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Big\ Sur' + script_loc + ' --volume /Volumes/Install\ macOS\ Big\ Sur --nointeraction')),
	"Catalina": Version("Catalina", 10, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Catalina' + script_loc + ' --volume /Volumes/Install\ macOS\ Catalina --nointeraction')),
	"Mojave": Version("Mojave", 10, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Mojave' + script_loc + ' --volume /Volumes/Install\ macOS\ Mojave --nointeraction')),
	"High Sierra": Version("High Sierra", 10, r'echo ' + password + ' | sudo -S {}'.format(installer_loc + '/Install\ macOS\ High\ Sierra' + script_loc + ' --volume /Volumes/Install\ macOS\ High\ Sierra --nointeraction'))
}

# Get the versions the user would like to install
selected_versions = select_versions(disk_name, disk_size)
# Partition the drives according to the selected versions
partition_drive(selected_versions, versions, disk_label)


# Loop through the selected versions and execute the install commands associated with them
for version in selected_versions:
	volume_path = "/Volumes/Install\ macOS\ " + version.replace(" ", "\ ") 
	command = versions[version].command
	thread = Thread(target=runInstallCommand, args=(command,))
	threads.append(thread)
	thread.start()

# Once we have threads associated with each OS install, attempt to execute the commands simultaneously
for index, thread in enumerate(threads):
 	thread.join()
