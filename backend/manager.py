import os
import subprocess
import signal
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Chave de API para proteção simples do manager
MANAGER_API_KEY = "nordes_manager_secret_key_9988"

def check_auth():
    key = request.headers.get('X-Manager-Key')
    return key == MANAGER_API_KEY

# Caminho para o app.py do backend
BACKEND_APP = os.path.join(os.path.dirname(__file__), 'app.py')

def get_backend_pid():
    try:
        # Procura por processos python que estejam rodando o app.py
        output = subprocess.check_output(["pgrep", "-f", "python.*app.py"]).decode().strip()
        if output:
            return int(output.split('\n')[0])
    except:
        return None
    return None

@app.route('/', methods=['GET'])
def index():
    return """
    <div style='font-family: sans-serif; text-align: center; padding: 50px; background: #030013; color: white; min-height: 100vh;'>
        <h1 style='color: #00d4ff;'>Nordes Manager API</h1>
        <p>Este serviço está rodando corretamente.</p>
        <p>Para gerenciar o backend, utilize a página: <b>public/pages/control.html</b></p>
        <hr style='width: 50%; border: 0.5px solid #333; margin: 30px auto;'>
        <p style='font-size: 0.8rem; color: #888;'>Rotas disponíveis: /status, /start, /stop</p>
    </div>
    """

@app.route('/status', methods=['GET'])
def status():
    pid = get_backend_pid()
    return jsonify({
        "status": "online" if pid else "offline",
        "pid": pid
    })

@app.route('/start', methods=['POST'])
def start():
    if not check_auth():
        return jsonify({"message": "Não autorizado"}), 401
    pid = get_backend_pid()
    if pid:
        return jsonify({"message": "Backend já está rodando", "status": "online"}), 200
    
    try:
        # Inicia o backend em um novo processo
        log_file = open(os.path.join(os.path.dirname(__file__), 'flask.log'), 'a')
        subprocess.Popen(["python3", BACKEND_APP], stdout=log_file, stderr=log_file)
        time.sleep(2) # Espera um pouco para o processo iniciar
        return jsonify({"message": "Backend iniciado com sucesso", "status": "online"}), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao iniciar: {str(e)}", "status": "offline"}), 500

@app.route('/stop', methods=['POST'])
def stop():
    if not check_auth():
        return jsonify({"message": "Não autorizado"}), 401
    pid = get_backend_pid()
    if not pid:
        return jsonify({"message": "Backend já está desligado", "status": "offline"}), 200
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        return jsonify({"message": "Backend desligado com sucesso", "status": "offline"}), 200
    except Exception as e:
        return jsonify({"message": f"Erro ao desligar: {str(e)}", "status": "online"}), 500

if __name__ == '__main__':
    app.run(port=5001)
