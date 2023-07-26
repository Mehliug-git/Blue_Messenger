#!/usr/bin/python3

import re
import argparse
import os
import bluetooth
import sys
import time
import tempfile
import time


# Temp directory for output
temp_dir = tempfile.mkdtemp()

counter = 0
scan_duration = 5

ble_list_name = []
ble_list_addr = []

# Setting the color combinations
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
BOLD_BLUE = "\033[2;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"


def main():
    print(
f"""
{BLUE}@@@@@@@   @@@       @@@  @@@  @@@@@@@@                 @@@@@@@@@@   @@@@@@@@   @@@@@@    @@@@@@   @@@@@@@@  @@@  @@@   @@@@@@@@  @@@@@@@@  @@@@@@@   
@@@@@@@@  @@@       @@@  @@@  @@@@@@@@                 @@@@@@@@@@@  @@@@@@@@  @@@@@@@   @@@@@@@   @@@@@@@@  @@@@ @@@  @@@@@@@@@  @@@@@@@@  @@@@@@@@  
@@!  @@@  @@!       @@!  @@@  @@!                      @@! @@! @@!  @@!       !@@       !@@       @@!       @@!@!@@@  !@@        @@!       @@!  @@@  
!@   @!@  !@!       !@!  @!@  !@!                      !@! !@! !@!  !@!       !@!       !@!       !@!       !@!!@!@!  !@!        !@!       !@!  @!@  
{RESET}{BOLD_BLUE}@!@!@!@   @!!       @!@  !@!  @!!!:!                   @!! !!@ @!@  @!!!:!    !!@@!!    !!@@!!    @!!!:!    @!@ !!@!  !@! @!@!@  @!!!:!    @!@!!@!   
!!!@!!!!  !!!       !@!  !!!  !!!!!:                   !@!   ! !@!  !!!!!:     !!@!!!    !!@!!!   !!!!!:    !@!  !!!  !!! !!@!!  !!!!!:    !!@!@!    
!!:  !!!  !!:       !!:  !!!  !!:                      !!:     !!:  !!:            !:!       !:!  !!:       !!:  !!!  :!!   !!:  !!:       !!: :!!   
:!:  !:!   :!:      :!:  !:!  :!:                      :!:     :!:  :!:           !:!       !:!   :!:       :!:  !:!  :!:   !::  :!:       :!:  !:!  
 :: ::::   :: ::::  ::::: ::   :: ::::  :::::::::::::  :::     ::    :: ::::  :::: ::   :::: ::    :: ::::   ::   ::   ::: ::::   :: ::::  ::   :::  
:: : ::   : :: : :   : :  :   : :: ::   :::::::::::::   :      :    : :: ::   :: : :    :: : :    : :: ::   ::    :    :: :: :   : :: ::    :   : :  
{RESET}
""")
    # for the --help
    parser = argparse.ArgumentParser(description='Bluetooth Messenger script for send a message to anyone with Bluetooth !')
    args = parser.parse_args()

    #sudo verification
    if not os.geteuid() == 0:
        print(BOLD, RED,f"[!] SUDO requied, please make a sudo command",RESET)
        sys.exit()
    else:
        global new_name
        new_name = input("[?] Choose your message :")

        #start bluetooth service
        os.system("systemctl start bluetooth")
        pass
main()


def filter_lines_with_new(output):

    lines = output.split('\n')
    new_lines = [line for line in lines if "NEW" in line]

    #avoir une liste avec numéro     
    tmp_list = [f'{num + 1} {line}' for num, line in enumerate(new_lines)]
    numbered_output = '\n'.join(tmp_list)


    #var pour la selection de la MAC en fonction du choix user
    listes = [line.split() for line in new_lines]

    print(numbered_output) #tmp_list

    while True:
        try:
            numero_ligne = int(input("[?] Choose the number of the target (1 to {}): ".format(len(listes))))
            if 1 <= numero_ligne <= len(listes):
                break
            else:
                print(BOLD, RED,f"[!] Wrong number, please retry",RESET)
        except ValueError:
            print(BOLD, RED,f"[!] Please insert a valid number",RESET)

    # Afficher la liste correspondant à la ligne demandée par l'utilisateur
    ligne_demandee = listes[numero_ligne - 1]


    return ligne_demandee



def detecter_adresse_mac(data):
    pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
    match = re.search(pattern, data)
    if match:
        return match.group()
    else :
        print(BOLD, RED,"[!] No match found",RESET)
        sys.exit()


# Find MAC address bluetooth
def discover_bluetooth_devices():
    global device_name
    os.system(f"bluetoothctl --timeout {scan_duration} scan on > {temp_dir}/scan.txt")
    
    #open result file    
    with open(f"{temp_dir}/scan.txt", "r") as file:
        scan_out = file.read()
    
    
    #For only select lines with "NEW"
    data = filter_lines_with_new(scan_out)
    # Delete all elements after the 3rd for exclude name in scope result 
    data = data[:3]
    device_name = data[3:]

    data = ''.join(str(item) for item in data)

    #Filter for MAC address (for detect with the fucking colors flags )
    test = detecter_adresse_mac(data)
    return test




# Change bluetooth name
def change_computer_name(new_name):
    new_name = f'"{new_name}"'
    os.system(f"hciconfig hci0 name '{new_name}'")
    time.sleep(2)

# Bluetooth connexion fonction
def connect_bluetooth(device_name, device_address):
    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((device_address, 1))
        print(GREEN,f"[+] Connected to {device_name} with MAC : {device_address}", RESET)
        return socket
    except bluetooth.btcommon.BluetoothError as err:
        print(BOLD, RED,f"[!] Failed to connect:", err, RESET)
        return None

#Bluetooth pair fonction
def pair_bluetooth(device_address):
    counter =+ 1

    #obligé de faire os.system en raison des regele de secu de subprocess
    os.system(f"bluetoothctl pair {device_address} > {temp_dir}/output.txt")
    
    # Lecture du contenu du fichier de sortie
    with open(f"{temp_dir}/output.txt", "r") as file:
        output = file.read()
    
    # Vérification de la présence de "not available" dans la sortie
    if "not available" in output:
        print(counter)
        os.system("systemctl force-reload bluetooth")
        time.sleep(2)
        pair_bluetooth(device_address)
    else:
        pass


# Find and print bt MAC addresss 
print("[+] Try to find Bluetooth devices...")
#MAC address choice
device_address = discover_bluetooth_devices()


# Change bluetooth name
print(f"[+] Change Bluetooth name to : {new_name}...")
change_computer_name(new_name)


# Bluetooth pairing
print(f"[+] Connect to {device_name} MAC : {device_address}")

pair_bluetooth(device_address)

if device_address:
    socket = connect_bluetooth(device_name, device_address)
    if socket:
        # Faire quelque chose avec le socket Bluetooth
        # Par exemple, envoyer des données
        socket.send("Hello bitch !")
        socket.close()


#start bluetooth service
os.system("bluetoothctl scan off && systemctl stop bluetooth")