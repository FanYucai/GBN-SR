import socket
from netlib1 import getseq
import os
import random


def sendterminalsg(sdsocket, val=-2):
    expseq = val
    if random.randint(0, 5) != 0:
        sdsocket.sendto("seq:" + str(expseq) + "\r\n\r\n", dest)
    acknowledged = False
    ctnto = 0
    while not acknowledged:
        try:
            ACK, address = sdsocket.recvfrom(1024)
            ctnto = 0
            # print ACK
            ackseq = getseq(ACK)
            # print ackseq
            # print expseq
            if ackseq == expseq:
                acknowledged = True
        except socket.timeout:
            ctnto += 1
            if random.randint(0, 5) != 0:
                sdsocket.sendto("seq:" + str(expseq) + "\r\n\r\n", dest)
            if ctnto == 10:
                break


class linknode():

    def __init__(self,seq):
        self.seq = seq
        self.chk = False
        self.next = None

def init_windows():
    global base
    global user_input
    global expseq
    global sdsocket
    global tail
    global expseq_tl
    global raw_str
    global dest
    curptr = base
    for i in range(0, 15):
            if not user_input:
                break
            user_input = 'seq:' + str(expseq) + '\r\n\r\n' + user_input
            if random.randint(0, 5) != 0:
                sdsocket.sendto(user_input, dest)
            if i == 0:
                continue
            else:
                curptr.next=linknode(expseq)                
                curptr=curptr.next
                tail = curptr
            expseq = expseq_tl
            expseq_tl = min(expseq + PKTFIXEDLEN, len(raw_str))
            user_input = raw_str[expseq:expseq_tl]

def slide():
    global user_input
    global expseq
    global sdsocket
    global expseq_tl
    global raw_str
    global dest
    if not user_input:
        return linknode(-1)
    user_input = 'seq:' + str(expseq) + '\r\n\r\n' + user_input
    if random.randint(0, 5) != 0:
        sdsocket.sendto(user_input, dest)
    retnode = linknode(expseq)
    expseq = expseq_tl    
    expseq_tl = min(expseq + PKTFIXEDLEN, len(raw_str))
    user_input = raw_str[expseq:expseq_tl]
    return retnode

def resend():
    global base
    global raw_str
    global sdsocket
    global dest
    curptr = base
    while curptr:
        tmpend=min(curptr.seq+PKTFIXEDLEN,len(raw_str))
        print 'resend seq:' + str(curptr.seq)
        if random.randint(0, 5) != 0 and not curptr.chk:
            sdsocket.sendto('seq:' + str(curptr.seq) + '\r\n\r\n' +raw_str[curptr.seq:tmpend], dest)
        curptr = curptr.next

base = linknode(0)
tail = base
N = 15


PREFIX = ""
if os.name == 'nt':
    PREFIX = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '\\'
PKTFIXEDLEN = 512
sdsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sdsocket.settimeout(0.5)
print 'destip:',
destaddr = raw_input()
dest = (destaddr, 88)
raw_str = ''
expseq = 0
print "filename:",
filename = raw_input()
with open(os.name == 'nt' and PREFIX + filename or filename, 'rb') as f:
    raw_str = f.read()
expseq_tl = min(expseq + PKTFIXEDLEN, len(raw_str))
# print raw_str
user_input = raw_str[expseq:expseq_tl]


#print expseq
# print expseq_tl
init_windows()
#acknowledged = False
#seqchgfg = False

while True:
    try:
        if base.seq==-1:
            break
        ACK, address = sdsocket.recvfrom(1024)
        print repr(ACK)
        ackseq = getseq(ACK)

        # print ackseq
        print 'nextseq:'+str(expseq)    
        curptr = base    
        while curptr.seq < ackseq and curptr.seq != -1:
            #print 'base:'+str(base.seq)
            curptr=curptr.next 
        if base.seq == ackseq: 
            base.chk = True
            while base.chk :           
                base = base.next
                tail.next= slide()
                if tail.next.seq == -1:
                    print 'EOF!'
                else:
                    tail = tail.next
                    print 'slide a window!'  
        elif curptr.seq == ackseq:
            curptr.chk = True     
    except socket.timeout:
        print 'timeout!'
        resend()
print repr(ACK)
# if not seqchgfg:
#    expseq = expseq_tl

sendterminalsg(sdsocket)
sendterminalsg(sdsocket, -3)
sdsocket.close()
