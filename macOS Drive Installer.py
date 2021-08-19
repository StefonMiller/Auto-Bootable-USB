"""
	Please feel free to edit this to your heart's content!

	with love
	- Kevin C
"""

from sys import stderr, stdout, stdin
import subprocess, re
import glob, shutil
from threading import Thread

def runInstallCommand(command):
	stdin.flush()
	stdout.flush()
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	(out, err) = p.communicate()
	print(out.decode(), err.decode())


#TODO Auto-format and partition USB to standardized names.
#TODO Ensure USB is not being used by other processes(Maybe force eject/remount drive) to avoid "Error erasing disk error number (-69888, 0)"
#TODO Allow for arbitrary macOS version names, much easier once we can standardize partition names

threads = []

stop = 'y'

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

