#!/usr/bin/python3

import re
import argparse
import os
#import bluetooth
import sys
import time
import tempfile
import time


# Temp directory for output
temp_dir = tempfile.mkdtemp()

counter = 0

send_counter = 0 #counter for numbers of times you want to pair with the targer (for flood)

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
        global spam_counter
        message_input = f"{BOLD}{BLUE}[?] Choose your message : {RESET}"
        spam_counter_msg = f"{BOLD}{BLUE}[?] How often do I pair to the target ? [FOR SPAM OR NOT] : {RESET}"

        new_name = input(message_input)
        spam_counter = int(input(spam_counter_msg))

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

            message_num = f"{BOLD}{BLUE},[?] Choose the number of the target (1 to {format(len(listes))}): {RESET}"
            numero_ligne = int(input(message_num))
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
print(BOLD, BLUE,"[+] Try to find Bluetooth devices...",RESET)
#MAC address choice
device_address = discover_bluetooth_devices()


# Change bluetooth name
print(BOLD, BLUE,f"[+] Change Bluetooth name to : {new_name}...",RESET)
change_computer_name(new_name)


# Bluetooth pairing
print(BOLD, BLUE,f"[+] Connect to {device_name} MAC : {device_address}",RESET)

while send_counter < spam_counter:
    send_counter += 1
    pair_bluetooth(device_address)

#start bluetooth service
os.system("bluetoothctl scan off && systemctl stop bluetooth")