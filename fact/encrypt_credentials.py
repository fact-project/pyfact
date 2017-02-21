from getpass import getpass
import simplecrypt

def decrypt(inpath, outpath):
    password = getpass()
    with open(inpath, 'rb') as infile, open(outpath, 'wb') as outfile:
        outfile.write(
            simplecrypt.decrypt(password, infile.read())
            )


def encrypt(inpath, outpath):
    password = getpass()
    with open(inpath, 'rb') as infile, open(outpath, 'wb') as outfile:
        outfile.write(
            simplecrypt.encrypt(password, infile.read())
        )

