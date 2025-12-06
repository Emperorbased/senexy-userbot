from flask import Flask, render_template, request, jsonify
import json
import secrets
import sys
app = Flask(name)
app.secret_key = secrets.token_hex(32)
sessions_data = {}
@app.route('/')
def index():
sid = request.args.get('session')
if not sid or sid not in sessions_data:
return "Invalid", 403
return render_template('setup.html')
@app.route('/api/stepint:s', methods=['POST'])
def handle_step(s):
data = request.json
sid = data.get('session_id')
if not sid or sid not in sessions_data:
return jsonify({'error': 'Invalid'}), 403
keys = ['api_id', 'api_hash', 'phone', 'password']
if s <= len(keys):
sessions_data[sid][keys[s-1]] = data.get(keys[s-1])
return jsonify({'success': True})
@app.route('/api/complete', methods=['POST'])
def complete():
data = request.json
sid = data.get('session_id')
if not sid or sid not in sessions_data:
return jsonify({'error': 'Invalid'}), 403
sd = sessions_data[sid]
creds = {
'api_id': sd.get('api_id'),
'api_hash': sd.get('api_hash'),
'phone': sd.get('phone'),
'password': sd.get('password', ''),
'code': data.get('code'),
'prefix': '.'
}
with open('credentials.json', 'w') as f:
json.dump(creds, f, indent=2)
return jsonify({'success': True})
if name == 'main':
if len(sys.argv) > 1:
sid = sys.argv[1]
sessions_data[sid] = {}
else:
sid = secrets.token_urlsafe(16)
sessions_data[sid] = {}
app.run(host='0.0.0.0', port=5000, debug=False)
