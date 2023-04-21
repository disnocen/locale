#! /usr/bin/python3
from flask import Flask, request, render_template, jsonify
from pymerkle import MerkleTree, verify_inclusion
# import pickle
import dill
import os
import subprocess
import hashlib
import datetime
import urllib.request
import random

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = './files'

merkle_tree = MerkleTree()
token_list = []


def print_debug(message):
    if app.debug:
        print(message)


def update_list(l, b, d):
    if b not in l:
        raise ValueError(f"{b} not found in list")
    index_of_b = l.index(b)
    l[index_of_b] = d
    return l


def _rand_num_as_string():
    num = random.randrange(0, 2**30)
    return str(num)


def _download_merkle_tree(url):

    num = _rand_num_as_string()
    filename = "merkle_file_dl_"+num+".obj"
    print_debug("Downloading merkle tree form url" + str(url))
    urllib.request.urlretrieve(url, filename)
    print_debug("Donwload complete")
    print_debug("Reading merkle tree downloaded file")
    with open(filename, 'rb') as f:
        dl_merkle_tree_file = f.read()
    print_debug("Reading complete")
    print_debug("Trying to upload the serialized data....")
    M = dill.loads(dl_merkle_tree_file)
    print_debug("Uploading in RAM complete")
    return M


def _upload_file(filename):
    print_debug(f"Uploading file {filename} on IPFS")
    output = subprocess.check_output(
        ['./node_modules/.bin/w3', 'up', filename])
    return output


def replace_node(data_old, data_new):
    merkle_tree_new = MerkleTree()

    token_list_new = update_list(token_list, data_old, data_new)

    for i in range(len(token_list)):
        merkle_tree_new.append_entry(token_list_new[i])

    return token_list_new, merkle_tree_new


def is_hex(text):
    try:
        int(text, 16)
        return True
    except ValueError:
        raise ValueError("Input is not a valid hexadecimal string")


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = uploaded_file.filename
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        output = subprocess.check_output(
            ['./node_modules/.bin/w3', 'up', filename])
        return render_template('res.html', output=output.decode())
    return render_template('index.html')


@app.route('/add_node', methods=['POST'])
def add_node():
    global token_list
    global merkle_tree

    # Get the new node value from the POST request
    new_node = request.form['new_node']

    milliseconds = datetime.datetime.now().timestamp() * 1000

    node_with_date = f"{new_node}{milliseconds}"

    hashed_node = hashlib.sha256(node_with_date.encode()).digest()
    token_list.append(hashed_node)

    # Add the new node to the Merkle tree
    merkle_tree.append_entry(hashed_node)

    # Get the new root hash
    new_root = merkle_tree.root

    # Return the new root hash as JSON
    output = f'the token is {hashed_node.hex()}'

    num = _rand_num_as_string()

    token_list_filename = "./curr_token_list" + num + ".obj"
    merkle_tree_filename = "./curr_merkle_tree" + num + ".obj"

    with open(token_list_filename, "wb") as f1:
        f1.write(dill.dumps(token_list))
    with open(merkle_tree_filename, "wb") as f2:
        f2.write(dill.dumps(merkle_tree))

    link_curr_token_list = _upload_file(token_list_filename)
    link_curr_merkle_tree = _upload_file(merkle_tree_filename)

    return render_template('res.html', output=f"token {output} added\nThe merkle tree is at {link_curr_merkle_tree}")
    return render_template('res.html', output=output)


@app.route('/check_inclusion', methods=['POST'])
def check_inclusion():

    token_hex = request.form['token']
    is_hex(token_hex)
    token = bytes.fromhex(token_hex)

    proof = merkle_tree.prove_inclusion(token)
    target = merkle_tree.root
    try:
        verify_inclusion(token, target, proof)
        ret = True
    except InvalidChallenge:
        ret = False

    return render_template('res.html', output=f"{ret}. the root of Merkle tree is {target.decode()}")


@app.route('/retrieve', methods=['GET', 'POST'])
def check_inclusion_retrieve():

    if request.method == 'POST':
        token_hex = request.form['token']
        is_hex(token_hex)
        token = bytes.fromhex(token_hex)
        ipfs_url = request.form['url']

        dl_merkle_tree = _download_merkle_tree(ipfs_url)

        proof = dl_merkle_tree.prove_inclusion(token)
        target = dl_merkle_tree.root
        try:
            verify_inclusion(token, target, proof)
            ret = True
        except InvalidChallenge:
            ret = False

        return render_template('res.html', output=f"{ret}. the root of Merkle tree is {target.decode()}")
    elif request.method == 'GET':
        return render_template('retrieve.html')
    else:
        return render_template('res.html', output=f"no request method supplied")


@app.route('/get_tree', methods=['POST'])
def get_tree():
    return render_template('res.html', output=merkle_tree)


@app.route('/spend_token', methods=['POST'])
def spend_token():
    token_hex = request.form['token']
    is_hex(token_hex)
    token = bytes.fromhex(token_hex)
    global token_list
    global merkle_tree

    token_list, merkle_tree = replace_node(token, b'void')
    num = _rand_num_as_string()

    token_list_filename = "./curr_token_list" + num + ".obj"
    merkle_tree_filename = "./curr_merkle_tree" + num + ".obj"

    with open(token_list_filename, "wb") as f1:
        f1.write(dill.dumps(token_list))
    with open(merkle_tree_filename, "wb") as f2:
        f2.write(dill.dumps(merkle_tree))

    link_curr_token_list = _upload_file(token_list_filename)
    link_curr_merkle_tree = _upload_file(merkle_tree_filename)
    return render_template('res.html', output=f"token {token_hex} spent\nThe merkle tree is at {link_curr_merkle_tree}/{merkle_tree_filename}")


app.run()
