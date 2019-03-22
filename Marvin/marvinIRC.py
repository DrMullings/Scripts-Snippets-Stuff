#!/usr/bin/env python3

import sys
import socket
import string

HOST = "irc.freenode.net"
PORT = 6667
CHANNEL = "##jrauch-bottest"

NICK = "jrauch-TestBot"
MASTER = "jrauch"

s = socket.socket()
s.connect((HOST, PORT))

s.send(bytes("USER " + NICK + " " + NICK + " " + NICK + " " + NICK + "\n", "UTF-8"))
s.send(bytes("NICK " + NICK + "\n", "UTF-8"))

def joinChan(chan):
    s.send(bytes("JOIN " + chan + "\n", "UTF-8"))
    ircmsg = ""
    while ircmsg.find("End of /NAMES list.") == -1:
        ircmsg = s.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)

def sendMsg(msg, target=CHANNEL): # sends messages to the target.
    s.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))



def main():
    joinChan(CHANNEL)
    sendMsg("Hello there", CHANNEL)
    while 1:
        ircmsg = s.recv(1024).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)
        #TODO strip down all the overhead
        sendMsg(ircmsg, CHANNEL)

main()
