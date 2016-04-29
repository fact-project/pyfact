from getpass import getpass
from simplecrypt import encrypt


with open('credentials.ini', 'rb') as infile:
    config = infile.read()

with open('fact_credentials/credentials.encrypted', 'wb') as outfile:
    password = getpass()
    outfile.write(encrypt(password, config))
