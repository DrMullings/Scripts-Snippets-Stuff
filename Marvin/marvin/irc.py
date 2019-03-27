#!/usr/bin/env python3

import sys
import socket
import string
from queue import Queue
import threading
from time import sleep
import re
import pdb

class IRC(object):
    def __init__(self, host, port, channel, nick, github):
        self.host = host
        self.nick = nick
        self.port = int(port)
        self.channel = channel
        self.nick = nick
        self.github = github
        self.s = socket.socket()
        self.establish_connection()
        self.join_chan(channel)

        self._txqueue = Queue(maxsize=1)

        self._running = True

        self._transmitter = threading.Thread(target=self._tramsmit)
        self._transmitter.setDaemon(True)
        self._transmitter.start()

        self._receiver = threading.Thread(target=self._receive)
        self._receiver.setDaemon(True)
        self._receiver.start()

    def establish_connection(self):
        self.s.connect((self.host, self.port))
        self.s.send(bytes("USER " + self.nick + " " + self.nick + " " + self.nick + " " + self.nick + "\n", "UTF-8"))
        self.s.send(bytes("NICK " + self.nick + "\n", "UTF-8"))

    def join_chan(self, chan):
        self.s.send(bytes("JOIN " + chan + "\n", "UTF-8"))
        ircmsg = ""
        while ircmsg.find("End of /NAMES list.") == -1:
            ircmsg = self.s.recv(2048).decode("UTF-8")
            ircmsg = ircmsg.strip('\n\r')
            print(ircmsg)

    def send_msg(self, msg, target=None):
        target = target or self.channel
        self._txqueue.put("PRIVMSG "+ target +" :"+ msg +"\n")

    def pong(self):
        self._txqueue.put("PONG :pingis\n")

    def _tramsmit(self):
        while self._running:
            msg = self._txqueue.get()
            self.s.send(bytes(msg, "UTF-8"))
            sleep(1)

    def _receive(self):
        while self._running:
            ircmsg = self.s.recv(1024).decode("UTF-8")
            ircmsg = ircmsg.rstrip('\n\r')
            #print(ircmsg)
            if 'PING' in ircmsg:
                self.pong()

            if ircmsg.find("PRIVMSG") != -1:
                name = ircmsg.split('!',1)[0][1:]
                message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
                
                if re.search(r"https://github\.com/[^/]+/[^/]+/pull/[0-9]+", message):
                    m = re.search(r'https://github\.com/(?P<org>[^/]+)/(?P<repo>[^/]+)/pull/(?P<id>[0-9]+)', message)
                    pr_id = m.group('id')
                    pr_repo =  m.group('repo')
                    pr_org = m.group('org')
                   
                    try:
                        pr = self.github.g.get_organization(pr_org).get_repo(pr_repo).get_pull(int(pr_id))
                        age = self.github.last_comment_age(pr)
                        if self.github.is_merged(pr):
                            self.send_msg("PR is already merged")
                        else:
                            self.send_msg("PR is stalled since " + str(age) + " days")
                    except Exception as e:
                        print(e)
                        #pdb.set_trace()
                        self.send_msg("An error occured: " + str(e.status) + ": " + e.data.get('message'))

