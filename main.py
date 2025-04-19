from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret-key-123'

ADMIN_USERNAME = 'adminv2login'
ADMIN_PASSWORD = '798290'

# All 15 keys with durations and device limits
KEYS = {
    'QLBSL81ZBYTB': {"type": "1M", "devices": 1, "expires": datetime.now() + timedelta(days=30), "used_devices": [], "blocked": False},
    'VPU77IJI0BXL': {"type": "1M", "devices": 1, "expires": datetime.now() + timedelta(days=30), "used_devices": [], "blocked": False},
    '561CKCJMMK3A': {"type": "1M", "devices": 1, "expires": datetime.now() + timedelta(days=30), "used_devices": [], "blocked": False},
    '9OUJYYCR5ALL': {"type": "1M", "devices": 1, "expires": datetime.now() + timedelta(days=30), "used_devices": [], "blocked": False},
    'XGPLAD02K96R': {"type": "1M", "devices": 1, "expires": datetime.now() + timedelta(days=30), "used_devices": [], "blocked": False},

    'GAEOQNXJQI9J': {"type": "2M", "devices": 3, "expires": datetime.now() + timedelta(days=60), "used_devices": [], "blocked": False},
    '43VYB5VJYLM9': {"type": "2M", "devices": 3, "expires": datetime.now() + timedelta(days=60), "used_devices": [], "blocked": False},
    '9R45OIJKZ71Q': {"type": "2M", "devices": 3, "expires": datetime.now() + timedelta(days=60), "used_devices": [], "blocked": False},
    'T16CIBJ4AL79': {"type": "2M", "devices": 3, "expires": datetime.now() + timedelta(days=60), "used_devices": [], "blocked": False},
    'SP7U5AVLNM5H': {"type": "2M", "devices": 3, "expires": datetime.now() + timedelta(days=60), "used_devices": [], "blocked": False},

    'D578B8LNI61D': {"type": "3M", "devices": 5, "expires": datetime.now() + timedelta(days=90), "used_devices": [], "blocked": False},
    'I35OF878G4ES': {"type": "3M", "devices": 5, "expires": datetime.now() + timedelta(days=90), "used_devices": [], "blocked": False},
    'WM7LIP73XR09': {"type": "3M", "devices": 5, "expires": datetime.now() + timedelta(days=90), "used_devices": [], "blocked": False},
    'PC9ZLK2VITSI': {"type": "3M", "devices": 5, "expires": datetime.now() + timedelta(days=90), "used_devices": [], "blocked": False},
    'G4F2FO6CUSA2': {"type": "3M", "devices": 5, "expires": datetime.now() + timedelta(days=90), "used_devices": [], "blocked": False},
}

active_sessions = []
blocked_devices = []

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        if data['username'] == ADMIN_USERNAME and data['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return jsonify({'success': True})
        return jsonify({'success': False})
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/status')
def status():
    if not session.get('admin'): return "Unauthorized", 401
    active = sum(1 for key in KEYS if not KEYS[key]['blocked'] and KEYS[key]['expires'] > datetime.now())
    expired = sum(1 for key in KEYS if KEYS[key]['expires'] < datetime.now())
    blocked = sum(1 for key in KEYS if KEYS[key]['blocked'])
    return jsonify({"active_keys": active, "expired_keys": expired, "blocked_keys": blocked})

@app.route('/user-details')
def user_details():
    if not session.get('admin'): return "Unauthorized", 401
    return jsonify(active_sessions)

@app.route('/blocked-devices')
def get_blocked():
    if not session.get('admin'): return "Unauthorized", 401
    return jsonify({'blocked': blocked_devices})

@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_json()
    key = data['key']
    device_id = data['device_id']
    if device_id in blocked_devices:
        return jsonify({'error': 'This device is blocked'}), 403
    if key not in KEYS:
        return jsonify({'error': 'Invalid key'}), 400
    key_data = KEYS[key]
    if key_data['blocked']:
        return jsonify({'error': 'This key is blocked'}), 400
    if device_id in key_data['used_devices']:
        return jsonify({'message': 'Key activated successfully'})
    key_data['used_devices'] = [device_id]
    active_sessions.append({
        'key': key,
        'device_id': device_id,
        'ip': data['ip'],
        'country': data['country'],
        'phone': data['phone'],
        'os': data['os'],
        'time': datetime.now().isoformat()
    })
    return jsonify({'message': 'Key activated successfully (device reset)'})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if not session.get('admin'): return "Unauthorized", 401
    data = request.get_json()
    device_id = data['device_id']
    global active_sessions
    key_to_remove = None
    active_sessions = [s for s in active_sessions if not (s['device_id'] == device_id and (key_to_remove := s['key']))]
    if key_to_remove and device_id in KEYS[key_to_remove]['used_devices']:
        KEYS[key_to_remove]['used_devices'].remove(device_id)
    return jsonify({'message': f'Device {device_id} disconnected and key removed.'})

@app.route('/block-device', methods=['POST'])
def block():
    if not session.get('admin'): return "Unauthorized", 401
    device_id = request.get_json()['device_id']
    if device_id not in blocked_devices:
        blocked_devices.append(device_id)
    return jsonify({'message': f'Device {device_id} blocked'})

@app.route('/unblock-device', methods=['POST'])
def unblock():
    if not session.get('admin'): return "Unauthorized", 401
    device_id = request.get_json()['device_id']
    if device_id in blocked_devices:
        blocked_devices.remove(device_id)
        return jsonify({'message': f'Device {device_id} unblocked'})
    return jsonify({'error': 'Device not found in block list'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
