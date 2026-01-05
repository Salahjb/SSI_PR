import os
import subprocess
import json
import datetime

# Liste pour stocker les resultats pour le rapport JSON (T12.2)
audit_results = {
    "timestamp": str(datetime.datetime.now()),
    "project": "Projet Securite Zero Trust",
    "tests": []
}

def log_result(test_id, description, status):
    # 1. Affichage Console (T12.1)
    color = "\033[92m" if status == "PASS" else "\033[91m"
    print(f"Test {test_id} - {description}: {color}{status}\033[0m")
    
    # 2. Stockage pour le fichier (T12.2)
    audit_results["tests"].append({
        "id": test_id,
        "description": description,
        "status": status
    })

def check_process(process_name):
    try:
        subprocess.check_call(["pgrep", "-f", process_name], stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def check_logs():
    try:
        # Verifie dmesg ou syslog pour les traces FW_DROP
        cmd = "sudo dmesg | grep 'FW_DROP'"
        output = subprocess.check_output(cmd, shell=True)
        if len(output) > 0: return True
    except:
        pass
    return False

print("--- STARTING AUTOMATED AUDIT (Task 12) ---")

# --- EXECUTION DES TESTS ---

# Test Web Services
if check_process("secure_server.py"):
    log_result("T3.1", "Service Web Secure (HTTPS) Actif", "PASS")
else:
    log_result("T3.1", "Service Web Secure (HTTPS) Actif", "FAIL")

# Test VPN
if check_process("openvpn"):
    log_result("T5.2", "Service VPN (OpenVPN) Actif", "PASS")
else:
    log_result("T5.2", "Service VPN (OpenVPN) Actif", "FAIL")

# Test Firewall Logging
if check_logs():
    log_result("T2.4", "Journalisation Pare-feu (Logs)", "PASS")
else:
    log_result("T2.4", "Journalisation Pare-feu (Logs)", "FAIL")

# Test Snort IDS
if check_process("snort"):
    log_result("T7.1", "Service IDS (Snort) Actif", "PASS")
else:
    log_result("T7.1", "Service IDS (Snort) Actif", "FAIL")

print("--- AUDIT COMPLETE ---")

# --- GENERATION DU RAPPORT (T12.2) ---
report_filename = "audit_report.json"
with open(report_filename, "w") as f:
    json.dump(audit_results, f, indent=4)

print(f"\n[+] Rapport genere avec succes : {report_filename}")
print("[+] Contenu du rapport JSON :")
os.system(f"cat {report_filename}")
