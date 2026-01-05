import subprocess
import time
import re

# File to monitor
LOG_FILE = "/var/log/snort/alert"
BLOCKED_IPS = set()

def follow(thefile):
    thefile.seek(0, 2) # Go to the end of the file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

print("--- IPS ACTIVATED: Monitoring Snort Logs ---")

try:
    logfile = open(LOG_FILE, "r")
    lines = follow(logfile)
    for line in lines:
        # Check if it is one of our alerts (T7.1 or T7.3)
        if "T7.1" in line or "T7.3" in line:
            try:
                # Extract IP (Format: {PROTO} Source -> Dest)
                # We split by "->" and take the last part of the left side
                parts = line.split("->")[0].strip().split(" ")
                attacker_ip = parts[-1]

                # Sanity check to avoid blocking ourselves or empty strings
                if len(attacker_ip) > 6 and attacker_ip not in BLOCKED_IPS:
                    print(f"[!!!] ALERT DETECTED from {attacker_ip}")
                    print(f"[+] Applying Firewall Rule: DROP {attacker_ip}...")

                    # Block FORWARD (LAN Access) and INPUT (Router Access)
                    subprocess.call(["iptables", "-I", "FORWARD", "-s", attacker_ip, "-j", "DROP"])
                    subprocess.call(["iptables", "-I", "INPUT", "-s", attacker_ip, "-j", "DROP"])

                    BLOCKED_IPS.add(attacker_ip)
                    print(f"[OK] {attacker_ip} is now BANNED.")
            except Exception as e:
                print(f"Error parsing log: {e}")
except FileNotFoundError:
    print(f"Error: {LOG_FILE} not found. Is Snort running?")
