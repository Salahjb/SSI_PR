#!/bin/bash
# 0. Flush existing rules
iptables -F
iptables -X

# 1. Zero Trust Policy (Block Everything by Default)
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 2. Allow Loopback and Established Connections
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. Allow VPN Connection (WAN -> Router Input)
iptables -A INPUT -i r1-eth0 -p udp --dport 1194 -j ACCEPT

# 4. Allow VPN Tunnel Traffic (Trusted VPN -> Internal)
iptables -A INPUT -i tun0 -j ACCEPT
iptables -A FORWARD -i tun0 -j ACCEPT

# 5. DMZ Access Rules
# Allow HTTP (80) for Redirection
iptables -A FORWARD -i r1-eth0 -o r1-eth1 -p tcp --dport 80 -j ACCEPT
# Allow HTTPS (443) for Secure Web
iptables -A FORWARD -i r1-eth0 -o r1-eth1 -p tcp --dport 443 -j ACCEPT

# 6. LAN / Admin Rules 
# Allow Admin to talk TO the Router (Ping, SSH)
iptables -A INPUT -i r1-eth2 -j ACCEPT
# Allow Admin to talk THROUGH the Router (Internet Access)
iptables -A FORWARD -i r1-eth2 -j ACCEPT

# 7. Logging 
iptables -A FORWARD -j LOG --log-prefix "FW_DROP: " --log-level 4
iptables -A INPUT -j LOG --log-prefix "FW_INPUT_DROP: " --log-level 4
