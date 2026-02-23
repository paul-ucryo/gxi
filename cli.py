#!/usr/bin/env python3
#from serial import *
from socket import *
from time import sleep
import sys

'''Notes
look into RA - record array
'''

ERR={
    0:"No Error",
    1:"unrecognized command",
    7:"Cmd not valid while running",
    20:"Begin not valid with motor off",
    21:"Begin not valid while running",
    22:"Begin not possble due to Limit Switch",
}

SWCH = {
    0:"Latched",
    1:"Home Switch Status",
    2:"RLSW status inactive if high",
    3:"FWSW status inactive if high",
    4:"Undefined",
    5:"Axis Motor off if High",
    6:"Axis error exceeds error limit if high",
    7:"Axis in motion if high",
}
def swch(val):
    for i in SWCH:
        if i in (0,4,5,6):
            print(f'{SWCH[7-i]}: {val//2**(7-i)}')
        val = val%2**(7-i)
usb=0
#a=Serial(f'/dev/ttyUSB{usb}',baudrate=115200,timeout=.2)
a=socket(AF_INET,SOCK_DGRAM)
addr0=('10.0.100.5',1234)
addr1=('127.0.0.1',1234)

try:a.bind(addr0)
except OSError: a.bind(addr1)

bf0 = ''
#mt = '2.0'
sp = '2000'
sp2 = '40000'
sp3 = '1000'
#g0 = ('10.0.100.10',1234)
g0 = ('10.0.100.11',1234)
lpBack = ('127.0.0.1',1235)
def msg(msg):
    def fn():
        #print(msg)
        _msg = msg.encode('utf-8')
        try:a.sendto(_msg,g0);bf=a.recvfrom(4096)[0]
        except: 
            print('send to loopback')
            a.sendto(_msg,lpBack);bf=a.recvfrom(4096)[0]
        #print(bf)
        #a.write(_msg.encode('utf-8'));bf=a.read(1000)
        return bf
    return fn
#init = msg('MT ?\r\n')
#init = msg(f'MT {mt},{mt},-{mt},{mt};SP {sp},{sp},{sp},{sp};CN=1;LD 3,3,3,3;AG 1,0,0,0;SH\r\n')
axis = {'A':"aperature",'B':'filter','C':'linear','D':'carousel'}

#init = msg(f'MT 2.0,2.0,-2.0,2.5;SP {sp},{sp},{sp2},{sp3};CN 1,-1;LD 3,3,0,3;AG 0,0,0,1\r\n')
init = msg(f'MT 2.0,2.0,-2.0,2.5;SP {sp},{sp},{sp2},{sp3};CN 1,-1;LD 3,3,0,3;AG 0,0,0,2\r\n')
fw = msg("JGB=100000;BGB\r\n")
rst = msg('PRD=-500;BGD\r\n')
cw = msg('CN ,-1;PRD=15000;BGD\r\n')
ccw = msg('CN ,1;PRD=-15000;BGD\r\n')
fe = msg('FED;BGD\r\n')
mv = msg('PRD=250;BGD\r\n')
cls = msg('JGC=-4000;BGC\r\n')
opn = msg('JGC=4000;BGC\r\n')
st = msg('ST\r\n')
mo = msg('MO\r\n')
jg = msg('LDC=1;PRC=1000;BGC\r\n')
#jog = msg('JGA=5000;BGA\r\n')
jog = msg('JG 5000,500,0,500;BG\r\n')
#ld = msg('LDC=3\r\n')
#tp = msg('MG _PAA,_TPB,_TPC,_TPD\r\n')
tp = msg('PA ?,?,?,?\r\n')
pr = msg(f'SHA;PR 128000;BGA\r\n')
def swch0(val):
    for i in SWCH:
        if i in (0,4,5,6):
            print(f'{SWCH[7-i]}: {val//2**(7-i)}')
        val = val%2**(7-i)
    return val

def ts(): 
    try: a.sendto('TS\r\n'.encode('utf-8'),g0);bf=a.recvfrom(4096)[0]
    except: a.sendto('TS\r\n'.encode('utf-8'),lpBack);bf=a.recvfrom(4096)[0]
    print('\n-------------------\n')
    ls = []
    bf = bf.strip(b'\r\n:')
    bf = bf.split(b',') 
    try: 
        for i in range(len(bf)): 
            ls.append(int(bf[i]))
    except TypeError: pass
    for i in range(len(ls)): print('ABCD'[i]);swch(ls[i])

def tc():
    try: a.sendto('TC\r\n'.encode('utf-8'),g0);bf=a.recvfrom(4096)[0]
    except: a.sendto('TC\r\n'.encode('utf-8'),lpBack);bf=a.recvfrom(4096)[0]
    print('\n-------------------\n')
    ls = []
    bf = bf.strip(b'\r\n:')
    print(bf)
    print(ERR[int(bf)])

def s():
    st()
    mo()

def ts0(axis='C',i=3):
    try: a.sendto(f'TS {axis}\r\n'.encode('utf-8'),g0);bf=a.recvfrom(4096)[0]
    except: a.sendto(f'TS {axis}\r\n'.encode('utf-8'),lpBack);bf=a.recvfrom(4096)[0]
    bf = bf.strip(b'\r\n:')
    #print(bf)
    val = int(bf)
    #print(val%2**(i+1)//2**i)
    return val%2**(i+1)//2**i
    val = val//2**(i+1)  #2:rvs 3:fwd limit
    val = val%2**(i)  #2:rvs 3:fwd limit
    return val

d0 = msg(f'SHC;JGC=-{sp2};BGC\r\n')
clear = msg(f'SHC;JGC={sp2};BGC\r\n')
def dock():
    if ts0('D',1): d0()
    else:print('Carousel not in position')
usteps = 200*64
#hm_delta = ((4100,4100,0,100),('A','B','C','D'))
hm_offset = ((400,400,0,0),('A','B','C','D'))
#cells = (((usteps*(8*23/192)),(usteps*(8*23/192)),100,(usteps*(8/10))),('A','B','C','D'))
cells = (((usteps*(192/25)/8),(usteps*(192/25)/8),100,(usteps*(10)/8)),('A','B','C','D'))

def wait(axis):
    a0 = {'A':0,'B':1,'C':2,'D':3}[axis]
    while True:
        if ts0(axis,7): sleep(.5)
        else: break

def hm_check(axis):
    a0 = {'A':0,'B':1,'C':2,'D':3}[axis]
    if not ts0(axis,1): raise Exception("not home")
    '''
    while True:
        if not ts0(axis,1): sleep(.5)
        else: break
    '''
    _tp=msg(f'MG _PA{axis}\r\n')
    bf=_tp().strip(b':');
    pos=int(float(bf.strip()))
    delta = int(cells[0][a0])
    c0 = int((pos+1000)//delta)
    print(f'Cell: {c0}')
    if c0>0: d0 = pos-delta*c0
    else: d0 = pos-delta
    print(f'D0: {d0}')
    if abs(d0)>1000: return -1*pos
    return pos

def fw0():
    _m0 = msg(f'SHA;CN ,-1;PRA=2000;BGA\r\n')
    _m1 = msg(f'FEA;BGA\r\n')
    _m2 = msg(f'CN ,1;FEA;BGA\r\n')
    _m3 = msg(f'PRA=400;BGA\r\n')
    _m0();sleep(2);_m1()
    sleep(5)
    p0 = hm_check(0)
    print('in position')
    _m3()
    sleep(5)
    _m2()
    sleep(5)
    sleep(5)
    p1 = hm_check(0)
    print(f"{p1}-{p0}={p1-p0}")

    
    #print(f"hm: {hm_check(0)}")
    #if not hm_check(0): fw()
    #msg('DPA=0\r\n')()

def wheel(axis):
    a0 = {'A':0,'B':1,'C':2,'D':3}[axis]
    def fn():
        _m0 = msg(f'SH{axis};PR{axis}=2000;BG{axis}\r\n')
        _m1 = msg(f'FE{axis};BG{axis}\r\n')
        _m2 = msg(f'PR{axis}={hm_offset[0][a0]};BG{axis}\r\n')
        _m0();wait(axis);_m1();wait(axis)
        p0=hm_check(axis)
        print(f'p0: {p0}')
        #sleep(6)
        _m2()
        #p0=hm_check(axis)
        if p0<0: print("home");wait(axis);dp(axis)()
    return fn
fw=wheel('A')
aw=wheel('B')
cw=wheel('D')
'''
def fw():
    _m0 = msg(f'SHA;PRA=2000;BGA\r\n')
    _m1 = msg(f'FEA;BGA\r\n')
    _m2 = msg(f'PRA=400;BGA\r\n')
    _m0();sleep(2);_m1();
    p0=hm_check(0)
    print(f'p0: {p0}')
    #sleep(6)
    _m2()
    p0=hm_check(0)
    if p0<0: print("home");sleep(1);dpf()

def aw():
    _m0 = msg(f'SHB;PRB=2000;BGA\r\n')
    _m1 = msg(f'FEA;BGA\r\n')
    _m2 = msg(f'PRA=400;BGA\r\n')
    _m0();sleep(2);_m1();
    p0=hm_check(0)
    print(f'p0: {p0}')
    #sleep(6)
    _m2()
    p0=hm_check(0)
    if p0<0: print("home");sleep(1);dpf()
        


def ca():
    _m0 = msg(f'SHD;PRD=2000;BGD\r\n')
    _m1 = msg(f'FED;BGD\r\n')
    if not ts0('C',3): #m0();sleep(5);m1()
        _m0();sleep(2);_m1()
        #if not hm_check(3): ca()
    else: print("Stage is not clear")
'''

def dp(axis):
    #return msg(f'DP{axis}=30500\r\n')
    return msg(f'DP{axis}=4075\r\n')

dpf = dp('A')
dpa = dp('B')
dpc = dp('D')

fe=msg(f'SHA;FEA;BGA\r\n')
cli = {
    'init':init,
    'ts':ts,
    'tc':tc,
    'st':st,
    'mo':mo,
    'tp':tp,
    'pr':pr,
    'dock':dock,
    'clear':clear,
    'fe':fe,
    'fw0':fw0,
    'fw':fw,
    'aw':aw,
    'cw':cw,
    'dpa':dpa,
    'dpf':dpf,
    'dpc':dpc,
    #'hm':hm,
    #'x':hm2,
    #'ts0':ts0,
}

if __name__ == '__main__':
    st()
    init()
    try:
        while True:
            _in = input("cli$ ").strip()
            #try: print(cli[_in])
            try: cli[_in]()
            except KeyError:
                print('invalid command')
    except KeyboardInterrupt:print()
