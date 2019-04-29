import datetime
import os
import shutil
import sys
import json
import struct
from time import sleep

import maya
from twisted.logger import globalLogPublisher

from nucypher.characters.lawful import Alice, Bob, Ursula
from nucypher.data_sources import DataSource as Enrico
from nucypher.network.middleware import RestMiddleware
from nucypher.utilities.logging import simpleObserver
from umbral.keys import UmbralPublicKey

from werkzeug.utils import secure_filename

from flask import Flask
from flask import request, render_template, redirect, url_for
UPLOAD_FOLDER = './static/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


import re
import json
import ipfsapi

######################
# Boring setup stuff #
######################

# Execute the download script (download_finnegans_wake.sh) to retrieve the book
BOOK_PATH = os.path.join('.', 'finnegans-wake.txt')

# Twisted Logger
globalLogPublisher.addObserver(simpleObserver)

# Temporary file storage
TEMP_FILES_DIR = "{}/examples-runtime-cruft".format(os.path.dirname(os.path.abspath(__file__)))
TEMP_DEMO_DIR = "{}/finnegans-wake-demo".format(TEMP_FILES_DIR)
TEMP_CERTIFICATE_DIR = "{}/certs".format(TEMP_DEMO_DIR)

# Remove previous demo files and create new ones
shutil.rmtree(TEMP_FILES_DIR, ignore_errors=True)
os.mkdir(TEMP_FILES_DIR)
os.mkdir(TEMP_DEMO_DIR)
os.mkdir(TEMP_CERTIFICATE_DIR)

#######################################
# Finnegan's Wake on NuCypher Testnet #
# (will fail with bad connection) #####
#######################################

TESTNET_LOAD_BALANCER = "eu-federated-balancer-40be4480ec380cd7.elb.eu-central-1.amazonaws.com"

##############################################
# Ursula, the Untrusted Re-Encryption Proxy  #
##############################################
ursula = Ursula.from_seed_and_stake_info(host=TESTNET_LOAD_BALANCER,
                                         certificates_directory=TEMP_CERTIFICATE_DIR,
                                         federated_only=True,
                                         minimum_stake=0)

IPSF_CONN = ipfsapi.connect('127.0.0.1', 5001)


@app.route("/show")
def show():
    BOB.join_policy(label, alices_pubkey_bytes_saved_for_posterity)

    # Now that Bob has joined the Policy, let's show how Enrico the Encryptor
    # can share data with the members of this Policy and then how Bob retrieves it.
    with open(BOOK_PATH, 'rb') as file:
        finnegans_wake = file.readlines()
  
    for counter, plaintext in enumerate(finnegans_wake):

        #########################
        # Enrico, the Encryptor #
        #########################
        enciro = Enrico(policy_pubkey_enc=policy.public_key)

        # In this case, the plaintext is a
        # single passage from James Joyce's Finnegan's Wake.
        # The matter of whether encryption makes the passage more or less readable
        # is left to the reader to determine.
        single_passage_ciphertext, _signature = enciro.encapsulate_single_message(plaintext)
        data_source_public_key = bytes(enciro.stamp)
        del enciro

        ###############
        # Back to Bob #
        ###############

        enrico_as_understood_by_bob = Enrico.from_public_keys(
            policy_public_key=policy.public_key,
            datasource_public_key=data_source_public_key,
            label=label
        )

        # Now Bob can retrieve the original message.
        alice_pubkey_restored_from_ancient_scroll = UmbralPublicKey.from_bytes(alices_pubkey_bytes_saved_for_posterity)
        delivered_cleartexts = BOB.retrieve(message_kit=single_passage_ciphertext,
                                        data_source=enrico_as_understood_by_bob,
                                        alice_verifying_key=alice_pubkey_restored_from_ancient_scroll)

        # We show that indeed this is the passage originally encrypted by Enrico.
        assert plaintext == delivered_cleartexts[0]
        #print("Retrieved: {}".format(delivered_cleartexts[0]))	

@app.route("/share1")
def sharepage1():
	
    return render_template('share1.html')


@app.route("/upload", methods=['POST'])
def uploadfile():
    file = request.files['file']
    basedir = os.path.abspath(os.path.dirname(__file__))
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename)) 
        document = IPSF_CONN.add(basedir + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)    
    print (document)
    json_file = basedir + "/alice.json"
    with open(json_file, mode='r') as feedsjson:
        feeds = json.load(feedsjson)
    with open(json_file, mode='w') as feedsjson:
        json.dump([], feedsjson) 
    with open(json_file, mode='w') as feedsjson:
        feeds["Docs"].append(document)
        json.dump(feeds, feedsjson)
        feedsjson.close()
    with open(json_file, mode='r') as feedsjson:
        docs = json.load(feedsjson)
    login = "Alice"
    length = len(docs["Docs"])
    return render_template("main.html", login=login, docs=docs, length=length)


@app.route("/share", methods=['POST'])
def sharepage():
    hesh = request.form['Hash']
    name = request.form['Name']
    return render_template('share.html', hesh=hesh, name=name)

@app.route("/sharedoc", methods=['POST'])
def sharedoc():
    hesh = request.form['Hash']
    name = request.form['Name']
    basedir = os.path.abspath(os.path.dirname(__file__))
    share_file = basedir + "/share.json"
    document = {'Hash': hesh, 'Name': name}
    with open(share_file, mode='r') as feedsjson:
        feeds = json.load(feedsjson)
    with open(share_file, mode='w') as feedsjson:
        json.dump([], feedsjson) 
    with open(share_file, mode='w') as feedsjson:
        feeds["Docs"].append(document)
        json.dump(feeds, feedsjson)
        feedsjson.close()
    json_file = basedir + "/alice.json"
    with open(json_file, mode='r') as feedsjson:
        docs = json.load(feedsjson)         
    login = "Alice"
    length = 1
    return render_template('main.html', login=login, docs=docs, length=length)
    
@app.route("/addnewdoc")
def addnewdoc():
    return render_template('addnewdoc.html')


@app.route("/main", methods=['POST'])
def mainpage():
    login = request.form['login']
    basedir = os.path.abspath(os.path.dirname(__file__))
    json_file = basedir + "/alice.json"
    share_file = basedir + "/share.json"
    if login == "Alice":
        with open(json_file, mode='r') as feedsjson:
            docs = json.load(feedsjson)   
    else:
        #with open(share_file, mode='r') as feedsjson:
         #   docs = json.load(feedsjson)  
        # Here are our Policy details.
        json_string = """"""
        policy_end_datetime = maya.now() + datetime.timedelta(days=5)
        m, n = 2, 3  
        label = b"secret/files/and/stuff"

        ######################################
        # Alice, the Authority of the Policy # 
        ######################################
        ALICE = Alice(network_middleware=RestMiddleware(),
                      known_nodes=[ursula],
                      learn_on_same_thread=True,
                      federated_only=True,
                      known_certificates_dir=TEMP_CERTIFICATE_DIR)      
        BOB = Bob(known_nodes=[ursula],
                  network_middleware=RestMiddleware(),
                  federated_only=True,
                  start_learning_now=True,
                  learn_on_same_thread=True,
                  known_certificates_dir=TEMP_CERTIFICATE_DIR)

        ALICE.start_learning_loop(now=True)
        policy = ALICE.grant(BOB,
                             label,
                             m=m, n=n,
                             expiration=policy_end_datetime)

        # Alice puts her public key somewhere for Bob to find later...
        alices_pubkey_bytes_saved_for_posterity = bytes(ALICE.stamp)

        # ...and then disappears from the internet.    
        del ALICE
        
        BOB.join_policy(label, alices_pubkey_bytes_saved_for_posterity)

        # Now that Bob has joined the Policy, let's show how Enrico the Encryptor
        # can share data with the members of this Policy and then how Bob retrieves it.
        with open(share_file, 'rb') as file:
            finnegans_wake = file.readlines()
  
        for counter, plaintext in enumerate(finnegans_wake):
           #########################
           # Enrico, the Encryptor #
           #########################
           enciro = Enrico(policy_pubkey_enc=policy.public_key)

           # In this case, the plaintext is a
           # single passage from James Joyce's Finnegan's Wake.
           # The matter of whether encryption makes the passage more or less readable
           # is left to the reader to determine.
           single_passage_ciphertext, _signature = enciro.encapsulate_single_message(plaintext)
           data_source_public_key = bytes(enciro.stamp)
           del enciro

           ###############
           # Back to Bob #
           ###############
 
           enrico_as_understood_by_bob = Enrico.from_public_keys(
               policy_public_key=policy.public_key,
               datasource_public_key=data_source_public_key,
               label=label
           )

           # Now Bob can retrieve the original message.
           alice_pubkey_restored_from_ancient_scroll = UmbralPublicKey.from_bytes(alices_pubkey_bytes_saved_for_posterity)
           delivered_cleartexts = BOB.retrieve(message_kit=single_passage_ciphertext,
                                         data_source=enrico_as_understood_by_bob,
                                         alice_verifying_key=alice_pubkey_restored_from_ancient_scroll)

           # We show that indeed this is the passage originally encrypted by Enrico.
           assert plaintext == delivered_cleartexts[0] 
           json_string = json_string + format(delivered_cleartexts[0])
        
        #Replace excess chars from json-string after re-encrypt (or after update json-file)
        json_string1 = re.sub(r'\s+', ' ', json_string) 
        json_string1 = re.sub(r'$|\t|\n|\r', '', json_string1)         
        print(json_string1.replace('b\'', '').replace('\'', '"')) 
        jso = json_string1.replace('b\'', '').replace('}\'', '}')
        #Convert string to json & render a template
        docs = json.loads(jso)      
    length = len(docs["Docs"])
    return render_template('main.html', login=login, docs=docs, length=length)
 
 
    
@app.route("/")
def startpage():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
