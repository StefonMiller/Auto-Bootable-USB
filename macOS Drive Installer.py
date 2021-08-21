"""
	Please feel free to edit this to your heart's content!

	with love
	- Kevin C
"""
import os
from sys import stderr, stdout, stdin
import subprocess, re
import glob, shutil
from threading import Thread


class Version:
	def __init__(self, name, size, command):
		self.name = name
		self.size = size
		self.command = command

def runInstallCommand(command):
	stdin.flush()
	stdout.flush()
	p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	(out, err) = p.communicate()
	print(out.decode(), err.decode())

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
		disk_choice = input(output_str)
	
	return list(disks)[disk_choice-1], list(disks.values())[disk_choice-1], float(disk_size)

def format_disk(disk_label, disk_name):
	to_format = ""
	while(to_format != 'n' and to_format != 'y'):
		to_format = raw_input("\n\nAre you sure you want to format " + disk_name + "? (y/n)\n")

	if(to_format == 'y'):
		disk_name = disk_name.replace(" ", "\ ")
		command = "diskutil eraseDisk JHFS+ " + disk_name + " " + disk_label
		#os.system(command)
	else:
		exit(0)

def select_versions(name, size):
	print("\n\nDisk " + name + " has " + str(size) + " GB free")
	print("Please select the OS's you would like to install on the disk. Enter -1 to confirm selection:")
	selection = []
	i = 1
	for version in versions.values():
		print("\t" + str(i) + ". " +  version.name + " (" + str(version.size) + "GB)")
		i += 1
	entry = 0
	curr_size = 0
	while(entry != -1):
		entry = input("Currently installing: " + str(selection) + "\n")
		if(entry > 0 and entry <= len(versions.values())):
			temp = list(versions.values())[entry-1]
			if((curr_size + temp.size < size)):
				selection.append(temp.name)
				curr_size += temp.size
			else:
				print("Need " + str((curr_size + temp.size) - size) + " more GB to add " + temp.name)


#TODO Auto-format and partition USB to standardized names.
#TODO Ensure USB is not being used by other processes(Maybe force eject/remount drive) to avoid "Error erasing disk error number (-69888, 0)"
#TODO Allow for arbitrary macOS version names, much easier once we can standardize partition names

threads = []

stop = 'y'

disk_label, disk_name, disk_size = get_disk()
format_disk(disk_label, disk_name)

versions = {
	"Big Sur": Version("Big Sur", 13, ""),
	"Catalina": Version("Catalina", 10, ""),
	"Mojave": Version("Mojave", 10, ""),
	"High Sierra": Version("High Sierra", 10, ""),
	"Sierra": Version("Sierra", 10, ""),
	"El Capitan": Version("El Capitan", 10, "")
}

select_versions(disk_name, disk_size)


"""
while stop != 'y' and stop != 'n':
	stop = input("This installer script will currently only work for versions of macOS from High Sierra onwards. Continue? (y/n): ")
	stop = stop.lower()

if stop == 'y':

	installer_loc = r'/Applications/macOS\ Installers/'
	script_loc = '.app/Contents/Resources/createinstallmedia'

	keywords = [
		'Sur',
		'Monterey',
		'Catalina',
		'Mojave',
	]

	install_vols = {}

	for vol in glob.glob("/Volumes/*"):
		short_vol = vol[9:]
		for word in keywords:
			if re.search(r"{}".format(word.lower()), short_vol.lower()):
				split_short_vol = short_vol.split(' ')
				version = list(set(split_short_vol) & set(keywords)) # Finds the version meant for the volume
				if len(version) > 1 or version[0] == 'Sur':
					version = r'Big\ Sur' # Will need to be changed if future macOS versions have multiple words
				else:
					version = version[0]
				short_vol = r'Install\ macOS\ ' + version
				vol_split = vol.split(' ')
				vol = vol_split[0]
				for i in range(len(vol_split)-1):
					vol += r'\ ' + vol_split[i+1]
				install_vols[short_vol] = vol

	for version, volume_path in install_vols.items():
		usage_volume_path = volume_path.replace("\\", "")
		volume_usage = shutil.disk_usage(usage_volume_path)
		if volume_usage.used/volume_usage.total > .5:
			print(f'Volume \x1B[3m"{volume_path}"\x1B[0m is already used. Skipping.')
		else:
			command = r'echo cssd@pitt | sudo -S {}'.format(installer_loc + version + script_loc + ' --volume ' + volume_path + ' --nointeraction')
			thread = Thread(target=runInstallCommand, args=(command,))
			threads.append(thread)
			thread.start()

	for index, thread in enumerate(threads):
		thread.join()
"""
