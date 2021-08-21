"""
	Please feel free to edit this to your heart's content!

	with love
	- Kevin C
"""
import os
from sys import stderr, stdout, stdin
import subprocess, re
import glob
import shutil
from threading import Thread


class Version:
	def __init__(self, name, size, command):
		self.name = name
		self.size = size
		self.command = command

def runInstallCommand(command):
	p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

def get_disk():
	output_str = "Please select the flash drive to write installers to:\n"
	command = "diskutil list"
	lines = os.popen(command).read().split('\n')
	disks = {}
	disk_size = ""
	for line in lines:
		if(("/dev/disk" in line) and ("external" in line)):
			disks[(line.split(" ")[0])] = ""

	for disk in disks.keys():
		command = "diskutil info " + disk
		disk_info = os.popen(command).read().split('\n')
		for info in disk_info:
			if("Device / Media Name" in info):
				disks[disk] = " ".join(info.split(" ")[13:])
			if("Disk Size" in info):
				disk_size = " ".join(info.split(" ")[21:-6])


	num_disks = 1
	for disk in disks.values():
		output_str += (str(num_disks) + ":\t " + disk + '\n')
		num_disks += 1

	disk_choice = 999
	while(disk_choice > num_disks or disk_choice < 1):
		disk_choice = int(input(output_str))
	
	return list(disks)[disk_choice-1], list(disks.values())[disk_choice-1], float(disk_size)

def format_disk(disk_label, disk_name):
	to_format = ""
	while(to_format != 'n' and to_format != 'y'):
		to_format = input("\n\nAre you sure you want to format " + disk_name + "? (y/n)\n")

	if(to_format == 'y'):
		disk_name = disk_name.replace(" ", "\ ")
		command = "diskutil eraseDisk JHFS+ " + disk_name + " " + disk_label
		os.system(command)
	else:
		exit(0)

def select_versions(name, size):
	print("\n\nDisk " + name + " has " + str(size) + " GB free")
	print("Please select the OS's you would like to install on the disk. Enter -2 to clear and -1 to confirm selection:")
	selection = []
	i = 1
	for version in versions.values():
		print("\t" + str(i) + ". " +  version.name + " (" + str(version.size) + "GB)")
		i += 1
	entry = 0
	curr_size = 0
	while(entry != -1):
		entry = int(input("Currently installing: " + str(selection) + "\n"))
		if(entry > 0 and entry <= len(versions.values())):
			temp = list(versions.values())[entry-1]
			if(((curr_size + temp.size) < size) and (temp.name not in selection)):
				selection.append(temp.name)
				curr_size += temp.size
			elif((curr_size + temp.size) >= size):
				print("Need " + str((curr_size + temp.size) - size) + " more GB to add " + temp.name)
		elif(entry == -2):
			selection = []
			curr_size = 0
	
	return selection
	

def partition_drive(selected_versions, version_list, disk_label):
	command = "diskutil partitionDisk " + disk_label + " GPT " 
	for version in selected_versions:
		command += "JHFS+ Install\ macOS\ " + version.replace(" ", "\ ") + " " + str(version_list[version].size) + "g "

	os.system(command)	

#TODO Ensure USB is not being used by other processes(Maybe force eject/remount drive) to avoid "Error erasing disk error number (-69888, 0)"

threads = []

stop = 'y'

disk_label, disk_name, disk_size = get_disk()
format_disk(disk_label, disk_name)

installer_loc = r'/Applications/macOS\ Installers'
script_loc = '.app/Contents/Resources/createinstallmedia'

versions = {
	"Big Sur": Version("Big Sur", 13, r'echo cssd@pitt | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Big\ Sur' + script_loc + ' --volume /Volumes/Install\ macOS\ Big\ Sur --nointeraction')),
	"Catalina": Version("Catalina", 10, r'echo cssd@pitt | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Catalina' + script_loc + ' --volume /Volumes/Install\ macOS\ Catalina --nointeraction')),
	"Mojave": Version("Mojave", 10, r'echo cssd@pitt | sudo -S {}'.format(installer_loc + '/Install\ macOS\ Mojave' + script_loc + ' --volume /Volumes/Install\ macOS\ Mojave --nointeraction')),
	"High Sierra": Version("High Sierra", 10, r'echo cssd@pitt | sudo -S {}'.format(installer_loc + '/Install\ macOS\ High\ Sierra' + script_loc + ' --volume /Volumes/Install\ macOS\ High\ Sierra --nointeraction'))
}

selected_versions = select_versions(disk_name, disk_size)
partition_drive(selected_versions, versions, disk_label)

for version in selected_versions:
	volume_path = "/Volumes/Install\ macOS\ " + version.replace(" ", "\ ") 
	command = versions[version].command
	thread = Thread(target=runInstallCommand, args=(command,))
	print(command)
# 	threads.append(thread)
# 	thread.start()

# for index, thread in enumerate(threads):
# 	thread.join()
