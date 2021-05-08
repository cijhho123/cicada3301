##
# OpenSSL key generation module for futorcap.
# This file serves as a reference for additional keygen modules.
# The functions in this file need not guard against malicious args.

README = """
     __       _                              __       _                _
    / _|_   _| |_ ___  _ __ ___ __ _ _ __   / _|_   _| |_ ___  _ __ __| |
   | |_| | | | __/ _ \| '__/ __/ _` | '_ \ | |_| | | | __/ _ \| '__/ _` |
   |  _| |_| | || (_) | | | (_| (_| | |_) ||  _| |_| | || (_) | | | (_| |
   |_|  \__,_|\__\___/|_|  \___\__,_| .__(_)_|  \__,_|\__\___/|_|  \__,_|
                                    |_|

This directory contains a number of private and public keys with filenames which
include timestamps at certain intervals. The public keys are released a certain
amount of time before the private keys. It is impossible to obtain a private key
before the time specified in the public key filename. This capability can be
used to send messages which will be impossible to read until this time.


The .priv files in this directory are openssl "key files" and the .pub files
are openssl "cert files" in PEM format. Use the .pub keys to encrypt and .priv
keys to decrypt. You can encrypt like this:

openssl smime -encrypt -binary -aes-256-cbc -in plainfilename \\
        -out cipherfilename -outform DER 2014-02-20_05-13-33_UTC.pub

And decrypt like this:

openssl smime -decrypt -binary -in cipherfilename -inform DER \\
        -out plainfilename -inkey 2014-02-20_05-13-33_UTC.priv

The .pub files are all signed by root.pub. You should receive root.pub via a
secure channel and verify all other .pub files like this:

openssl verify -CAfile root.pub 2014-02-20_07-01-30_UTC.pub

Make sure to check that the cert's Common Name matches the filename.


    Powered by futorcap.futord ~ GPL2 Copyright 2014 Marcus Wanner
"""

import subprocess, os

##
# Do any root key setup. This will certainly be run before generate() and may
# be run often, so don't overwrite existing keys. You will get a keydir keyword
# arg which provides a location for your keys, along with a str-format keyword
# arg for each entry in your plugin's section of the config.
def init(keydir=".", bits="2048", instancename="Generic Futord Instance"):

    privroot = os.path.join(keydir, "root.priv")
    pubroot = os.path.join(keydir, "root.pub")

    makepubkey = False
    makeprivkey = False
    if not os.path.exists(privroot):
        makeprivkey = True
        makepubkey = True
    elif not os.path.exists(pubroot):
        makeprivkey = True
        makepubkey = True

    if makeprivkey:
        c = subprocess.call(["openssl", "genrsa", "-out", privroot, bits])
        assert c == 0, "Root privkey generation failed"
    if makepubkey:
        c = subprocess.call(
            "echo '"
                "[ req ]\n"
                "distinguished_name     = req_distinguished_name\n\n"
                "prompt                 = no\n"
                "[ req_distinguished_name ]\n"
                "O                      = futorcap.futord\n"
                "OU                     = {}\n"
                "CN                     = Futord Root' | "
                "openssl req -batch -config /dev/stdin -x509 -new -nodes"
                " -key {} -out {}"
                "".format(instancename, privroot, pubroot),
            shell=True)
        assert c == 0, "Root pubkey generation failed"

    open(os.path.join(keydir, "README.txt"), "w").write(README)

##
# Generate a privkey/pubkey pair. You will get a str-format keyword arg for
# each entry in your plugin's section of the config, along with a keydir where
# your keys will reside, in addition to the pubfname and privfname keyword
# args which specify the names of the files this function will write relative
# to the keydir.
def generate(pubfname=None, privfname=None, keydir=".",
        bits="2048", instancename="Generic Futord Instance"):

    assert pubfname is not None and privfname is not None, \
        "Both pubfname and privfname are required!"
    pubfname = os.path.join(keydir, pubfname)
    privfname = os.path.join(keydir, privfname)

    c = subprocess.call(["openssl", "genrsa", "-out", privfname, bits])
    assert c == 0, "Privkey generation failed"

    privroot = os.path.join(keydir, "root.priv")
    pubroot = os.path.join(keydir, "root.pub")
    shortname = os.path.split(pubfname)[1]
    c = subprocess.call(
        "echo '"
            "[ req ]\n"
            "distinguished_name     = req_distinguished_name\n\n"
            "prompt                 = no\n"
            "[ req_distinguished_name ]\n"
            "O                      = Futorcap\n"
            "OU                     = {}\n"
            "CN                     = {}' | "
            "openssl req -batch -config /dev/stdin -new -key {} | "
            "openssl x509 -req -CA {} -CAkey {} -CAcreateserial -out {}"
            "".format(instancename, shortname, privfname,
                        pubroot, privroot, pubfname),
        shell=True)
    assert c == 0, "Pubkey generation failed"
