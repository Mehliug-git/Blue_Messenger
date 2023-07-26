#!/usr/bin/python3

import re
import argparse
import os
import bluetooth
import sys
import time
import tempfile
import time

"""
HEHEHEHA :

94:D3:31:F8:BB:00 / Tel Android
DC:B7:2E:0A:97:4F / tel Kali







ca devrait marcher t'arrive bine a isoler la MAC manque plus que la connexion foncitonne bien hehe



"""
#dossier temp pour l'output
temp_dir = tempfile.mkdtemp()

counter = 0
scan_duration = 4

ble_list_name = []
ble_list_addr = []

# Setting the color combinations
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"


def main():
    print("""
            tmp
        """)
    # for the --help
    parser = argparse.ArgumentParser(description='Mass Deauth wifi script\n\n Give to the script the interface name and the monitor interface name [without this wlan0 by default]')
    args = parser.parse_args()

    #sudo verification
    if not os.geteuid() == 0:
        print(BOLD, RED,f"[!] SUDO requied, please make a sudo command")
        sys.exit()
    else:
        global new_name
        new_name = input("Choose your message :")

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
            numero_ligne = int(input("Choose the number of the target (1 to {}): ".format(len(listes))))
            if 1 <= numero_ligne <= len(listes):
                break
            else:
                print("Wrong number, please retry")
        except ValueError:
            print("Please insert a valide number")

    # Afficher la liste correspondant à la ligne demandée par l'utilisateur
    ligne_demandee = listes[numero_ligne - 1]


    return ligne_demandee



def detecter_adresse_mac(data):
    pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
    match = re.search(pattern, data)
    if match:
        return match.group()
    else :
        print("No match found")
        sys.exit()





# Trouver les adresses MAC des périphériques Bluetooth à proximité
def discover_bluetooth_devices():
    global device_name
    os.system(f"bluetoothctl --timeout {scan_duration} scan on > {temp_dir}/scan.txt")
    
    #open result file    
    with open(f"{temp_dir}/scan.txt", "r") as file:
        scan_out = file.read()
    
    
    #fonc pour select uniquement les lignes avec new detect
    data = filter_lines_with_new(scan_out)

    # sup des éléments après les 3 premiers commme ça on garde pas le nom peux importe cb d'éléments il prend se chien
    data = data[:3]
    device_name = data[3:]

    data = ''.join(str(item) for item in data)

    #filtre pour qu'il ne reste que la MAC add (avec les flag de couleurs)
    test = detecter_adresse_mac(data)
    return test




# Changer le nom de l'ordinateur
def change_computer_name(new_name):
    new_name = f'"{new_name}"'
    os.system(f"hciconfig hci0 name '{new_name}'")
    time.sleep(2)

# Se connecter au premier périphérique Bluetooth trouvé
def connect_bluetooth(device_name, device_address):
    try:
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        socket.connect((device_address, 1))
        print(f"Connected to {device_name} with MAC : {device_address}")
        return socket
    except bluetooth.btcommon.BluetoothError as err:
        print("Failed to connect:", err)
        return None


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
        print("HHAHAHAHAHAHAHHAA")



# Trouver et afficher les adresses MAC des périphériques Bluetooth à proximité
print("Recherche des périphériques Bluetooth à proximité...")
#choix addresse MAC
device_address = discover_bluetooth_devices()


# Changer le nom de l'ordinateur en "TEST_BLUE"
print(f"Changement du nom de l'ordinateur en {new_name}...")
change_computer_name(new_name)


# Se connecter au premier périphérique Bluetooth trouvé
print(f"Connect to {device_name} MAC : {device_address}")

pair_bluetooth(device_address)

if device_address:
    socket = connect_bluetooth(device_name, device_address)
    if socket:
        # Faire quelque chose avec le socket Bluetooth
        # Par exemple, envoyer des données
        socket.send("Hello, Bluetooth device!")
        socket.close()


#start bluetooth service
os.system("bluetoothctl scan off && systemctl stop bluetooth")

#Pas de connexion chacal