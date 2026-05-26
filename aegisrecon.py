#!/usr/bin/env python3
import sys
import os
import socket
import threading
import requests
from datetime import datetime
import json

# Terminal Colors for Kali Linux Theme
G = "\033[92m"  # Green
R = "\033[91m"  # Red
Y = "\033[93m"  # Yellow
B = "\033[94m"  # Blue
W = "\033[0m"   # White

def banner():
    print(f"""{B}
 ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄     ▄▄▄▄▄▄▄    ▄▄▄▄▄▄   ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄  
█       █       █       █   █   █       █  █      █ █       █       █       █      █ 
█   ▄   █    ▄▄▀█    ▄▄_█   █   █  ▄▄▄▄▄█  █  ▄    ██    ▄▄▄█   ▄   █   ▄   █  ▄    █
█   █▄█ █   █▄▄▄█   █▄▄▄█   █   █ █▄▄▄▄▄   █ █ █   ██   █▄▄▄█  █ █  █  █ █  █ █ █   █
█   ▄   █    ▄▄_█    ▄▄_█   █▄▄ █_     █   █ █▄█   ██    ▄▄▄█  █▄█  █  █▄█  █ █▄█   █
█  █ █  █   █▄▄▄█   █▄▄▄█       █▄▄▄▄▄  █  █       ██   █▄▄▄█       █       █       █
█▄_█ █▄_█▄▄▄▄▄▄_█▄▄▄▄▄▄_█▄▄▄▄▄▄_█▄▄▄▄▄▄_█  █▄▄▄▄▄▄_██▄▄▄▄▄▄_█▄▄▄▄▄▄_█▄▄▄▄▄▄_█▄▄▄▄▄▄_█
                            {G}[ Version 2.0 - Pure Python Engine ]{W}
    """)

# Global list to store open ports from multiple threads
open_ports = []
print_lock = threading.Lock()

def scan_port(ip, port):
    """Pure Python Socket Connection Logic"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)  # Connection timeout
        result = sock.connect_ex((ip, port))
        if result == 0:
            with print_lock:
                print(f"   {G}[+] Port {port:<5} is OPEN  --> {socket.getservbyname(port) if port in [21,22,23,25,53,80,443,445,3306,3389] else 'unknown'}{W}")
                open_ports.append(port)
        sock.close()
    except:
        pass

def start_threaded_scanner(ip):
    """Launches multi-threaded scan for extremely fast execution"""
    print(f"\n{Y}[*] Launching Pure Python Multi-Threaded Port Scanner...{W}")
    # Top critical ports used in penetration testing
    ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 1433, 3306, 3389, 8080, 8443]
    
    threads = []
    for port in ports_to_scan:
        t = threading.Thread(target=scan_port, args=(ip, port))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    if not open_ports:
        print(f"   {R}[-] No standard open ports discovered via stealth probe.{W}")

def native_dns_recon(domain):
    """Fetches core DNS IP architecture using python standard socket library"""
    print(f"{Y}[*] Resolving Target Domain via Native Sockets...{W}")
    try:
        ip_address = socket.gethostbyname(domain)
        print(f"   {G}[+] Target Primary IP: {ip_address}{W}")
        
        # Reverse Lookup
        try:
            host_info = socket.gethostbyaddr(ip_address)
            print(f"   {G}[+] Reverse DNS (Host): {host_info[0]}{W}")
        except socket.herror:
            host_info = ["N/A"]
            
        return ip_address, f"IP: {ip_address}\nHost: {host_info[0]}"
    except socket.gaierror:
        print(f"   {R}[-] Error: Unable to resolve domain. Check target URL or internet.{W}")
        return None, ""

def passive_subdomain_harvest(domain):
    """Queries certificate registries via JSON stream for passive hunting"""
    print(f"\n{Y}[*] Harvesting Subdomains via Digital Certificate Intel...{W}")
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    discovered_subs = set()
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            entries = response.json()
            for entry in entries:
                name = entry['name_value']
                # Clean up wildcard entries if any
                if "*" not in name:
                    discovered_subs.add(name)
            
            print(f"   {G}[+] Discovered {len(discovered_subs)} Unique Subdomains:{W}")
            for index, sub in enumerate(sorted(list(discovered_subs))[:10]):
                print(f"       -> {sub}")
            if len(discovered_subs) > 10:
                print(f"       ... and {len(discovered_subs) - 10} more targets logged.")
            return "\n".join(discovered_subs)
        else:
            return "No subdomains found."
    except:
        print(f"   {R}[-] Certificate index server unreachable. Skipping passive harvest.{W}")
        return "Harvest failed."

def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner()
    
    if len(sys.argv) < 3 or sys.argv[1] != "-d":
        print(f"{R}Usage:{W} python3 aegis_recon.py -d <target_domain>")
        print(f"{Y}Example:{W} python3 aegis_recon.py -d testphp.vulnweb.com")
        sys.exit(1)
        
    target_domain = sys.argv[2]
    print(f"{B}[+] Target Initialized: {target_domain}{W}\n")
    
    # 1. Native Python DNS Resolve
    ip, dns_report = native_dns_recon(target_domain)
    
    if ip:
        # 2. Pure Python Multi-Threaded Port Scan
        start_threaded_scanner(ip)
        
        # 3. Passive Subdomain Gathering
        subdomain_report = passive_subdomain_harvest(target_domain)
        
        # 4. Generate Professional Report
        filename = f"aegis_report_{target_domain}.txt"
        with open(filename, "w") as f:
            f.write(f"=== AEGIS-RECON CRIMINAL INTELLIGENCE REPORT ===\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target Domain: {target_domain}\n")
            f.write(f"Resolved IP: {ip}\n")
            f.write(f"\n[1] DNS LOGS:\n{dns_report}\n")
            f.write(f"\n[2] OPEN PORTS DISCOVERED:\n{', '.join(map(str, open_ports)) if open_ports else 'None'}\n")
            f.write(f"\n[3] SUBDOMAINS IDENTIFIED:\n{subdomain_report}\n")
        
        print(f"\n{B}[+] Audit complete. Core Python report compiled in: {filename}{W}")
    else:
        print(f"{R}[-] Recon aborted due to host resolution failure.{W}")

if __name__ == "__main__":
    main()
