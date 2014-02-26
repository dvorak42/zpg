import zephyr
import time
import re
import random
import string
import os
import subprocess
import sys

botname = "zpgbot"

class ZephyrBot:
    def __init__(self, name, clss):
        self.name = name
        zephyr.init()
        for cls in clss:
            for i in range(0,10):
                zephyr.Subscriptions().add((("un" * i) + cls, '*', '*'))

    def transmit(self, dest, inst, message, sender=None):
        if dest != "message":
            zephyr.ZNotice(cls=dest, sender=self.name, instance=inst, opcode='bot', message="%s\x00%s\n" % (self.name, message)).send()
        elif sender != None:
            self.personal(sender, message)

    def personal(self, dest, message):
        zephyr.ZNotice(recipient=dest, sender=self.name, instance="personal", opcode='bot', message="%s\x00%s\n" % (self.name, message)).send()

    def poll(self, onReceive):
        m = zephyr.receive(False)
        if m:
            [_, body] = m.message.split("\x00")
            onReceive(m.sender, m.cls, m.instance, body)

class ZPGBridge:
    def __init__(self, game, classes, runner):
        self.zephyr = ZephyrBot(botname, classes)
        self.game = game
        self.wid = self.getWindow()
        self.runner = runner

    def getWindow(self):
        p = subprocess.Popen(["xdotool", "search", "--name", "^" + self.game + "$"], stdout=subprocess.PIPE)
        sout,err = p.communicate()
        sout = sout.strip().split("\n")
        if len(sout) > 0:
            return sout[0]
        return ""

    def sendCommand(self, cmd):
        mapping = {"UP": "q", "DOWN": "w", "LEFT": "e", "RIGHT": "r", "SELECT": "t", "START": "y", "A": "u", "B": "i", "S_LEFT": "o", "S_RIGHT": "p", "TOGGLE_FF": "f"}
        if cmd.upper() in mapping:
            subprocess.call(["xdotool", "key", "--window", self.wid, "--delay", "100", mapping[cmd.upper()]])

    def processor(self, sender, cls, instance, msg):
        if msg.strip() == "stream":
            self.zephyr.transmit("zephyrplaysgames", "stream", "The stream is at tinyurl.com/zpgemerald")
        else:
            self.runner.runCommand(sender, msg, self.sendCommand)

    def run(self):
        while True:
            self.zephyr.poll(self.processor)
            time.sleep(1)


class DefaultRunner:
    def __init__(self):
        pass
    
    def runCommand(self, sender, msg, do):
        do(msg.strip().split("\n")[0].lower())

class TomRunner:
    def runCommand(self, sender, msg, do):
        cmds = 0
        for line in msg.strip().split("\n"):
            elt = line.split()
            if len(elt) > 1 and elt[1].isdigit():
                for i in range(int(elt[1])):
                    if cmds > 9:
                        return
                    do(elt[0])
                    cmds += 1
                    time.sleep(0.2)
            elif len(elt) > 0:
                if cmds > 9:
                    return
                do(elt[0])
                cmds += 1
                time.sleep(0.2)
        


p = TomRunner()
z = ZPGBridge(sys.argv[1], ["dvorak42-test", "zephyrplaysgames"], p)
z.run()
