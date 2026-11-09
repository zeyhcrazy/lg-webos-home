"""Testa navegação da Início da LG sem controle: injeta teclas no event1 (LGE RCU) e captura a tela.
Uso: python tvnav.py <pasta_saida> <seq>   ex.: seq = "cap:a0 LEFT cap:a1 UP cap:a2"
"""
import os, sys, time
import paramiko

OUT, SEQ = sys.argv[1], sys.argv[2].split()
KEYS = {'UP': 103, 'LEFT': 105, 'RIGHT': 106, 'DOWN': 108, 'OK': 28, 'BACK': 158, 'HOME': 102}

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(os.environ.get('TV_HOST','192.168.1.10'), username='root', password='alpine', timeout=10)  # alpine = senha padrao do Homebrew Channel
sf = c.open_sftp()


def sh(cmd, t=30):
    _, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')


def key(code):
    sh("python3 -c \"import struct,time\n"
       "f=open('/dev/input/event1','wb')\n"
       "w=lambda t,c,v:(f.write(struct.pack('llHHi',0,0,t,c,v)),f.flush())\n"
       f"w(1,{code},1);w(0,0,0);time.sleep(0.06);w(1,{code},0);w(0,0,0);f.close()\"")
    time.sleep(0.7)


def cap(name):
    r = sh("rm -f /tmp/nav.png; luna-send -n 1 -f luna://com.webos.service.capture/executeOneShot "
           "'{\"path\":\"/tmp/nav.png\",\"method\":\"DISPLAY\",\"width\":1920,\"height\":1080,\"format\":\"PNG\"}' 2>&1")
    for _ in range(10):
        if sh("[ -s /tmp/nav.png ] && echo ok").strip() == 'ok':
            break
        time.sleep(0.5)
    else:
        print('cap FALHOU:', r.strip()[:300])
        return
    dest = os.path.join(OUT, name + '.png')
    sf.get('/tmp/nav.png', dest)
    print('cap', dest)


os.makedirs(OUT, exist_ok=True)
for step in SEQ:
    if step.startswith('cap:'):
        cap(step[4:])
    else:
        key(KEYS[step])
        print('key', step)
