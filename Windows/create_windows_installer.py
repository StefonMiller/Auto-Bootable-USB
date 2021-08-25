from subprocess import check_output, Popen, PIPE
import time
import os

# Class encapsulating disk data
class Disk:
    # Initialize disk object
    # @Param name: disk name
    # @Param size: disk size
    def __init__(self, name, size):
        self.name = name
        self.size = size

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
def format_disk(disk_num):
    # Write commands to format and partition the disk to a txt file
    with open("commands.txt", "wt") as file:
        file.write("select disk " + str(disk_num) + "\n")
        file.write("clean\n")
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
    # Navigate to the iso's boot directory and set the bootsect to /nt60. Then copy the files from the iso to the disk
    command = iso + ": && cd boot && bootsect /nt60 " + disk + ": && " + "xcopy " + iso + ":\*.* "  + disk + ":\ /E /F /H"
    p = Popen(command, shell=True)
    p.communicate()

if __name__ == "__main__":
    # Path to Windows install iso
    iso_path = os.path.abspath("Windows.iso").replace("\\", "\\\\")
    # Display all disks to the user and have them select one to format
    disk_num = select_disk()
    # Format the disk using diskpart
    disk_label = format_disk(disk_num)
    
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