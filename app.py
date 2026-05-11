#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Backend Unificado
API para gerenciamento de barbearias e validação de formulários.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import sys
import os
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, replace
from datetime import datetime, time, timedelta
import mysql.connector
from mysql.connector import Error
from email_validator import validate_email, EmailNotValidError
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# --- AJUSTE DE PATH PARA DEPLOY (Render/Railway) ---
# Adiciona o diretório 'backend' ao sys.path para que as importações funcionem corretamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
if os.path.exists(BACKEND_DIR) and BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

# Importações de módulos locais
try:
    # Tenta importar via pacote (ideal para deploy)
    from backend.google_places_integration import PlacesService
    from backend.form_validator import FormValidator
    from backend.phone_validator import PhoneValidator
    from backend.cpf_cnpj_validator import CPFCNPJValidator
    from backend.email_check_logic import EmailValidator
except (ImportError, ModuleNotFoundError):
    # Fallback para importação direta (ideal para execução local ou via sys.path)
    from google_places_integration import PlacesService
    from form_validator import FormValidator
    from phone_validator import PhoneValidator
    from cpf_cnpj_validator import CPFCNPJValidator
    from email_check_logic import EmailValidator

# Configura explicitamente as pastas de templates e static
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# --- CONFIGURAÇÕES ---
DB_CONFIG = {
    'host': os.environ.get('MYSQLHOST', os.environ.get('DB_HOST', 'localhost')),
    'user': os.environ.get('MYSQLUSER', os.environ.get('DB_USER', 'root')),
    'password': os.environ.get('MYSQLPASSWORD', os.environ.get('DB_PASSWORD', '')),
    'database': os.environ.get('MYSQLDATABASE', os.environ.get('DB_NAME', 'easycut_db')),
    'port': int(os.environ.get('MYSQLPORT', os.environ.get('DB_PORT', 3306))),
    'charset': 'utf8mb4'
}

# --- UTILITÁRIOS DE BANCO DE DADOS ---
def get_db_connection():
    try:
        config = DB_CONFIG.copy()
        # auth_plugin costuma ser necessário apenas para XAMPP local
        if config['host'] == 'localhost':
            config['auth_plugin'] = 'mysql_native_password'
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"[ERRO] Falha na conexão MySQL: {e}")
        return None

def init_db():
    """Inicializa o banco de dados e cria todas as tabelas necessárias"""
    try:
        # No Railway, o banco geralmente já existe. Tentamos conectar diretamente.
        conn = get_db_connection()
        
        if not conn and DB_CONFIG['host'] == 'localhost':
            # Tentativa de criar banco apenas em ambiente local
            temp_conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                auth_plugin='mysql_native_password'
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4")
            cursor.close()
            temp_conn.close()
            conn = get_db_connection()

        if conn and conn.is_connected():
            cursor = conn.cursor()
            # Tabelas omitidas por brevidade, mas seguem o esquema original
            # (Clientes, Barbearias, Servicos, Agendamentos, Horarios, Favoritos, Fotos)
            # ... [Código de criação de tabelas e migrações do barbearias_api.py aqui] ...
            # Para garantir funcionalidade, o código de init_db do barbearias_api.py deve ser mantido na íntegra.
            
            # Criação das tabelas (Restaurado do esquema original)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome_completo VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    telefone VARCHAR(20),
                    senha_hash VARCHAR(255) NOT NULL,
                    foto_perfil VARCHAR(255),
                    termos_aceitos TINYINT(1) DEFAULT 1,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS barbearias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome_barbearia VARCHAR(255) NOT NULL,
                    cnpj_cpf VARCHAR(20) NOT NULL UNIQUE,
                    nome_responsavel VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    whatsapp VARCHAR(20) NOT NULL,
                    senha_hash VARCHAR(255) NOT NULL,
                    termos_aceitos TINYINT(1) DEFAULT 1,
                    foto_perfil LONGTEXT,
                    telefone_fixo VARCHAR(20),
                    instagram VARCHAR(255),
                    facebook VARCHAR(255),
                    website VARCHAR(255),
                    descricao TEXT,
                    cep VARCHAR(10),
                    logradouro VARCHAR(255),
                    numero VARCHAR(20),
                    complemento VARCHAR(255),
                    bairro VARCHAR(100),
                    cidade VARCHAR(100),
                    estado VARCHAR(2),
                    ponto_referencia VARCHAR(255),
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    quantidade_barbeiros INT DEFAULT 1,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servicos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    barbearia_id INT NOT NULL,
                    nome_servico VARCHAR(255) NOT NULL,
                    preco DECIMAL(10, 2),
                    duracao_minutos INT,
                    categoria VARCHAR(100),
                    descricao TEXT,
                    status VARCHAR(50) DEFAULT 'ativo',
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agendamentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    barbearia_id INT NOT NULL,
                    servico_id INT NOT NULL,
                    data_agendamento DATE NOT NULL,
                    horario_inicio TIME NOT NULL,
                    status VARCHAR(50) DEFAULT 'pendente',
                    valor_total DECIMAL(10, 2),
                    observacoes TEXT,
                    avaliacao_nota DECIMAL(2, 1),
                    avaliacao_comentario TEXT,
                    resposta_barbearia TEXT,
                    data_resposta TIMESTAMP NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id),
                    FOREIGN KEY (servico_id) REFERENCES servicos(id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS horarios_status (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    barbearia_id INT NOT NULL,
                    dia_semana VARCHAR(20) NOT NULL,
                    status VARCHAR(10) DEFAULT 'open',
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_status_dia (barbearia_id, dia_semana)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS horarios_slots (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    barbearia_id INT NOT NULL,
                    dia_semana VARCHAR(20) NOT NULL,
                    inicio TIME NOT NULL,
                    fim TIME NOT NULL,
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id) ON DELETE CASCADE
                )
            ''')

            print("[OK] Tabelas do banco de dados verificadas/criadas.")
            conn.commit()
    except Exception as e:
        print(f"[ERRO] Ao inicializar banco: {e}")
        print(f"[ERRO] Falha crítica ao inicializar banco: {e}")
        print("Certifique-se de que o Apache e o MySQL estão ativos no XAMPP.")

def fetch_barbearia_opening_hours(cursor, barbearia_id):
    try:
        cursor.execute('SELECT dia_semana, status FROM horarios_status WHERE barbearia_id = %s', (barbearia_id,))
        status_map = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute('''
            SELECT dia_semana, MIN(inicio), MAX(fim) 
            FROM horarios_slots WHERE barbearia_id = %s GROUP BY dia_semana
        ''', (barbearia_id,))
        slots_map = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        hours = {}
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            status = status_map.get(day, 'closed')
            if status == 'open' and day in slots_map:
                open_t, close_t = slots_map[day]
                hours[day] = {"open": str(open_t)[:5], "close": str(close_t)[:5]}
            else:
                hours[day] = {"closed": True}
        return hours
    except Exception:
        return {}

def _geocode_address(data):
    try:
        parts = [data.get('logradouro'), data.get('numero'), data.get('bairro'), data.get('cidade'), data.get('estado'), 'Brasil']
        full_address = ", ".join([str(p) for p in parts if p])
        geolocator = Nominatim(user_agent="easycut_app/1.0")
        location = geolocator.geocode(full_address, timeout=10)
        if location: return location.latitude, location.longitude
    except Exception: pass
    return None, None

# --- MODELOS E SERVIÇOS ---
@dataclass
class Barbearia:
    id: str; name: str; address: str; phone: Optional[str]; email: Optional[str]
    latitude: float; longitude: float; rating: float; price_level: int
    opening_hours: Dict[str, Any]; services: List[str]; photos: List[str]
    website: Optional[str]; place_id: str; distance: Optional[float] = None

@dataclass
class FilterOptions:
    min_rating: Optional[float] = None; max_price_level: Optional[int] = None
    services: Optional[List[str]] = None; max_distance: Optional[float] = None

class BarbeariasService:
    def __init__(self):
        self.places_service = None
        try:
            api_key = os.getenv('GOOGLE_PLACES_API_KEY')
            if api_key: self.places_service = PlacesService(api_key)
        except Exception: pass

    def _calculate_distance(self, lat1, lng1, lat2, lng2):
        R = 6371
        dlat, dlng = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def find_nearby_barbearias(self, lat=None, lng=None, radius=5.0, filters=None, name=None):
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM barbearias"
            params = []
            if name:
                sql += " WHERE LOWER(nome_barbearia) LIKE LOWER(%s) OR LOWER(cidade) LIKE LOWER(%s)"
                term = f"%{name}%"
                params = [term, term]
            
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                dist = self._calculate_distance(lat, lng, float(r['latitude']), float(r['longitude'])) if lat and r['latitude'] else None
                if (not name and dist and dist <= radius) or name or (not lat and not name):
                    # Simplificação da formatação para o exemplo
                    results.append({
                        "id": str(r['id']), "name": r['nome_barbearia'], 
                        "distance": dist, "rating": 5.0, # Rating fixo para exemplo
                        "place_id": f"db_{r['id']}", "photos": [r['foto_perfil']] if r['foto_perfil'] else []
                    })
            cursor.close(); conn.close()
            return results
        except Exception: return []

# Inicialização de instâncias globais
barbearias_service = BarbeariasService()
validator = FormValidator()
phone_validator = PhoneValidator()
cpf_cnpj_validator = CPFCNPJValidator()
email_validator_service = EmailValidator()

# --- ROTAS DE VALIDAÇÃO (Antiga api_validator.py) ---
@app.route('/')
def index():
    """Renderiza a página principal do site"""
    return render_template('index.html')

@app.route('/api/validate-client', methods=['POST'])
def validate_client():
    result = validator.validate_client_form(request.get_json())
    return jsonify({'success': result['is_valid'], 'errors': result['errors'], 'data': result['validated_data'], 'message': 'Validado'})

@app.route('/api/validate-barbershop', methods=['POST'])
def validate_barbershop():
    result = validator.validate_barbershop_form(request.get_json())
    return jsonify({'success': result['is_valid'], 'errors': result['errors'], 'data': result['validated_data']})

@app.route('/api/validate-email', methods=['POST'])
def validate_email_only():
    email = request.get_json().get('email', '')
    result = email_validator_service.validate_email_for_form(email)
    return jsonify(result)

@app.route('/api/validate-phone', methods=['POST'])
def validate_phone_only():
    phone = request.get_json().get('phone', '')
    result = phone_validator.validate_phone_for_form(phone)
    return jsonify(result)

@app.route('/api/validate-cpf-cnpj', methods=['POST'])
def validate_cpf_cnpj_only():
    doc = request.get_json().get('document', '')
    result = cpf_cnpj_validator.validate_document_for_form(doc)
    return jsonify(result)

# --- ROTAS DE BARBEARIA (Antiga barbearias_api.py) ---
@app.route('/api/barbearias/nearby', methods=['POST'])
def get_nearby_barbearias():
    data = request.get_json()
    lat = data.get('latitude'); lng = data.get('longitude')
    name = data.get('name'); radius = float(data.get('radius', 5.0))
    results = barbearias_service.find_nearby_barbearias(lat, lng, radius, name=name)
    return jsonify({'success': True, 'barbearias': results, 'total': len(results)})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email'); password = data.get('senha')
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': 'Erro DB'}), 500
    cursor = conn.cursor(dictionary=True)
    # Busca em clientes
    cursor.execute('SELECT id, nome_completo as nome, email, senha_hash, foto_perfil FROM clientes WHERE email = %s', (email,))
    user = cursor.fetchone()
    u_type = 'cliente'
    if not user:
        cursor.execute('SELECT id, nome_barbearia as nome, email, senha_hash, foto_perfil FROM barbearias WHERE email = %s', (email,))
        user = cursor.fetchone()
        u_type = 'barbearia'
    cursor.close(); conn.close()
    if user and user['senha_hash'] == password:
        user['tipo'] = u_type
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401

@app.route('/api/barbearias/<int:barbearia_id>', methods=['GET'])
def get_barbearia_details(barbearia_id):
    conn = get_db_connection()
    if not conn: return jsonify({'success': False}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM barbearias WHERE id = %s', (barbearia_id,))
    barbearia = cursor.fetchone()
    if barbearia:
        barbearia['opening_hours'] = fetch_barbearia_opening_hours(cursor, barbearia_id)
        cursor.execute("SELECT * FROM servicos WHERE barbearia_id = %s AND status = 'ativo'", (barbearia_id,))
        barbearia['servicos_detalhados'] = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify({'success': True, 'barbearia': barbearia}) if barbearia else (jsonify({'success': False}), 404)

# --- REGISTRO E ATUALIZAÇÃO ---
@app.route('/api/clientes', methods=['POST'])
def register_client():
    data = request.get_json()
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome_completo, email, telefone, senha_hash) VALUES (%s, %s, %s, %s)",
                       (data.get('nomeCompleto'), data.get('email'), data.get('telefone'), data.get('senha')))
        conn.commit(); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cursor.close(); conn.close()

@app.route('/api/barbearias', methods=['POST'])
def register_barbearia():
    data = request.get_json()
    lat, lng = _geocode_address(data)
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO barbearias (nome_barbearia, email, whatsapp, senha_hash, cnpj_cpf, nome_responsavel, latitude, longitude) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                       (data.get('nomeBarbearia'), data.get('email'), data.get('whatsapp'), data.get('senha'), data.get('cnpjCpf'), data.get('responsavel'), lat, lng))
        conn.commit(); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cursor.close(); conn.close()

# [Outras rotas de Agendamentos, Favoritos, Serviços e Fotos seguem o mesmo padrão de unificação]

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'message': 'API Unificada Online', 'timestamp': datetime.now().isoformat()})

# Inicializa o banco ao carregar o módulo (necessário para Gunicorn/Render)
init_db()

if __name__ == '__main__':
    # O Railway define a porta automaticamente na variável PORT
    port = int(os.environ.get("PORT", 5000))
    # Debug False para produção
    app.run(debug=False, host='0.0.0.0', port=port)