"""Envia LG-TV/home-mods/home.xml pra TV, remonta e recarrega a Início (um processo só).
Uso: python deploy_home.py [arquivo_xml]   -> imprime render ok/falha (via /tmp/var/log/home)
"""
import sys
import os, time
import paramiko

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'home.xml')
TAG = f'=== DEPLOY {int(time.time())} ==='


def conn():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(os.environ.get('TV_HOST','192.168.1.10'), username='root', password='alpine', timeout=8)  # alpine = senha padrao do Homebrew Channel apos o root
    return c


def run(c, cmd, t=20):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')


c = conn()
data = open(SRC, 'rb').read().replace(b'\r\n', b'\n')
run(c, 'sh /media/developer/home-mods/apply-home-mods.sh off')
with c.open_sftp().open('/media/developer/home-mods/home.xml', 'w') as f:
    f.write(data)
run(c, 'chmod 644 /media/developer/home-mods/home.xml; sh /media/developer/home-mods/apply-home-mods.sh')
run(c, f"echo '{TAG}' >> /tmp/var/log/home")
for _ in range(4):
    pids = run(c, 'pgrep -f com.webos.app.home').split()
    if not pids:
        break
    try:
        run(c, 'kill -9 ' + ' '.join(pids))
    except Exception:
        pass
    time.sleep(2)
try:
    run(c, "luna-send -n 1 -f luna://com.webos.applicationManager/launch '{\"id\":\"com.webos.app.home\"}'")
except Exception:
    pass
c.close()
time.sleep(8)
for _ in range(8):
    try:
        c = conn()
        break
    except Exception:
        time.sleep(3)
if not run(c, 'pgrep -f com.webos.app.home').strip():
    run(c, "luna-send -n 1 -f luna://com.webos.applicationManager/launch '{\"id\":\"com.webos.app.home\"}'")
    time.sleep(5)
ok = False
for _ in range(12):
    if 'shelf length' in run(c, f"awk '/{TAG}/{{f=1}} f' /tmp/var/log/home"):
        ok = True
        break
    time.sleep(2)
print('render ok:', ok, '| pids:', run(c, 'pgrep -f com.webos.app.home').split())
