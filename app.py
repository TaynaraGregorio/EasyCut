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
import logging
import os
import math
from decimal import Decimal
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict, replace
from datetime import datetime, time, timedelta, date
import mysql.connector
from mysql.connector import Error
from email_validator import validate_email, EmailNotValidError
# Configuração de log para o Render (aparecerá nos Logs do Dashboard)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
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
_cors_origins = os.environ.get('CORS_ORIGINS', '').strip()
if _cors_origins:
    CORS(app, origins=[o.strip() for o in _cors_origins.split(',') if o.strip()])
else:
    # Sem CORS_ORIGINS: permite qualquer origem (útil em dev); em produção defina CORS_ORIGINS com o domínio do frontend
    CORS(app)

# --- CONFIGURAÇÕES ---
DB_CONFIG = {
    'host': os.environ.get('MYSQLHOST')
    or os.environ.get('MYSQL_HOST')
    or os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('MYSQLUSER')
    or os.environ.get('MYSQL_USER')
    or os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD')
    or os.environ.get('MYSQL_PASSWORD')
    or os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('MYSQLDATABASE')
    or os.environ.get('MYSQL_DATABASE')
    or os.environ.get('DB_NAME', 'easycut_db'),
    'port': int(os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT') or os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
}

# --- UTILITÁRIOS DE BANCO DE DADOS ---
def get_db_connection():
    try:
        config = DB_CONFIG.copy()
        # auth_plugin costuma ser necessário apenas para XAMPP local
        if config['host'] in ('localhost', '127.0.0.1'):
            config['auth_plugin'] = 'mysql_native_password'
        else:
            # FreeSQLDatabase / MySQL remoto: TLS costuma ser obrigatório
            ssl_ca = os.environ.get('MYSQL_SSL_CA')
            if ssl_ca:
                config['ssl_ca'] = ssl_ca
            elif os.environ.get('MYSQL_SSL_DISABLED', '').lower() in ('1', 'true', 'yes'):
                config['ssl_disabled'] = True
            else:
                config['ssl_disabled'] = False
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

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS barbearia_fotos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    barbearia_id INT NOT NULL,
                    foto LONGTEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cliente_favoritos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT NOT NULL,
                    barbearia_id INT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_cliente_barbearia (cliente_id, barbearia_id),
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id) ON DELETE CASCADE
                )
            ''')

            try:
                cursor.execute('ALTER TABLE clientes MODIFY COLUMN foto_perfil LONGTEXT NULL')
            except Exception:
                pass

            try:
                cursor.execute('ALTER TABLE agendamentos ADD COLUMN duracao_total INT DEFAULT 30 AFTER horario_inicio')
                conn.commit()
            except Exception:
                pass

            print("[OK] Tabelas do banco de dados verificadas/criadas.")
            conn.commit()
    except Exception as e:
        print(f"[ERRO] Ao inicializar banco: {e}")
        print(f"[ERRO] Falha crítica ao inicializar banco: {e}")
        print("Verifique MYSQLHOST/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE (ou DB_*) e conectividade com o MySQL.")

def fetch_barbearia_opening_hours(cursor, barbearia_id):
    try:
        cursor.execute('SELECT dia_semana, status FROM horarios_status WHERE barbearia_id = %s', (barbearia_id,))
        status_map = {}
        for row in cursor.fetchall():
            if isinstance(row, dict):
                status_map[row['dia_semana']] = row['status']
            else:
                status_map[row[0]] = row[1]
        cursor.execute('''
            SELECT dia_semana, MIN(inicio) AS inicio, MAX(fim) AS fim
            FROM horarios_slots WHERE barbearia_id = %s GROUP BY dia_semana
        ''', (barbearia_id,))
        slots_map = {}
        for row in cursor.fetchall():
            if isinstance(row, dict):
                slots_map[row['dia_semana']] = (row['inicio'], row['fim'])
            else:
                slots_map[row[0]] = (row[1], row[2])
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

# --- UTILITÁRIOS DE SERIALIZAÇÃO E TEMPO (MIGRADOS) ---
def _json_safe(v: Any) -> Any:
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, (datetime, date)): return v.isoformat()
    if isinstance(v, timedelta):
        total = int(v.total_seconds())
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
    if isinstance(v, bytes): return v.decode("utf-8", errors="replace")
    return v

def _as_hhmm(val: Any) -> str:
    if val is None: return "00:00"
    if isinstance(val, timedelta):
        total = int(val.total_seconds()) % 86400
        return f"{total // 3600:02d}:{(total % 3600) // 60:02d}"
    s = str(val)
    return s[:5] if len(s) >= 5 else s

def _time_to_minutes(hhmm: str) -> int:
    parts = hhmm.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def _minutes_to_time(m: int) -> str:
    m = max(0, m) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"

def _weekday_key(d: date) -> str:
    return ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][d.weekday()]

def db_status_to_api(s: Optional[str]) -> str:
    m = {"pendente": "pending", "confirmado": "confirmed", "cancelado": "cancelled", "concluido": "completed"}
    return m.get(str(s or "").lower().strip(), "pending")

def api_status_to_db(s: str) -> str:
    m = {"pending": "pendente", "confirmed": "confirmado", "cancelled": "cancelado", "completed": "concluido"}
    return m.get(str(s or "").lower().strip(), "pendente")

def servico_db_status_to_api(status: Optional[str]) -> str:
    return "active" if str(status or "").lower() in ("ativo", "active") else "inactive"

def servico_api_status_to_db(status: Optional[str]) -> str:
    return "ativo" if (status or "active").lower() in ("active", "ativo") else "inativo"

def format_barbearia_address(row: Dict[str, Any]) -> str:
    parts = [row.get("logradouro"), row.get("numero"), row.get("bairro"), row.get("cidade"), row.get("estado")]
    return ", ".join(str(p) for p in parts if p)

def serialize_barbearia_for_template(cursor, row: Dict[str, Any], barbearia_id: int, fetch_hours_fn) -> Dict[str, Any]:
    out = {k: _json_safe(v) for k, v in row.items()}
    out["name"] = row.get("nome_barbearia") or ""
    out["address"] = format_barbearia_address(row)
    out["phone"] = row.get("whatsapp") or row.get("telefone_fixo") or ""
    out["description"] = row.get("descricao") or ""
    out["opening_hours"] = fetch_hours_fn(cursor, barbearia_id)
    
    cursor.execute("SELECT nome_servico FROM servicos WHERE barbearia_id = %s AND status = 'ativo'", (barbearia_id,))
    out["services"] = [r['nome_servico'] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
    
    photos = [str(row["foto_perfil"])] if row.get("foto_perfil") else []
    cursor.execute("SELECT foto FROM barbearia_fotos WHERE barbearia_id = %s LIMIT 20", (barbearia_id,))
    for r in cursor.fetchall():
        f = r['foto'] if isinstance(r, dict) else r[0]
        if f and str(f) not in photos: photos.append(str(f))
    out["photos"] = photos

    cursor.execute("SELECT AVG(avaliacao_nota) FROM agendamentos WHERE barbearia_id = %s AND avaliacao_nota IS NOT NULL", (barbearia_id,))
    avg_row = cursor.fetchone()
    res = avg_row['AVG(avaliacao_nota)'] if isinstance(avg_row, dict) else (avg_row[0] if avg_row else None)
    out["rating"] = float(res) if res is not None else 5.0
    out["price_level"] = 2
    return out

# --- HELPERS DE AGENDAMENTO ---
def _intervals_overlap(a0: int, a1: int, b0: int, b1: int) -> bool:
    return a0 < b1 and b0 < a1

def _serialize_review_row(r: Dict[str, Any], for_barber: bool) -> Dict[str, Any]:
    nome = r.get("nome_cliente") or "Cliente"
    base = {
        "id": r["id"],
        "clientName": nome,
        "clientInitial": (nome[0] or "?").upper(),
        "service": r.get("nome_servico") or "",
        "text": r.get("avaliacao_comentario") or "",
        "rating": int(float(r["avaliacao_nota"])) if r.get("avaliacao_nota") is not None else 0,
        "date": str(r.get("data_agendamento") or "")[:10],
        "hasResponse": bool(r.get("resposta_barbearia")),
        "response": r.get("resposta_barbearia"),
        "responseDate": r.get("data_resposta"),
    }
    if not for_barber:
        return {
            "clientName": base["clientName"],
            "rating": base["rating"],
            "text": base["text"],
            "hasResponse": base["hasResponse"],
            "response": base["response"],
            "responseDate": base["responseDate"],
        }
    return base

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
        if not conn:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT b.*,
                       (SELECT COUNT(*) FROM agendamentos a WHERE a.barbearia_id = b.id) AS appointment_count
                FROM barbearias b
            """
            params = []
            if name:
                sql += " WHERE LOWER(b.nome_barbearia) LIKE LOWER(%s) OR LOWER(b.cidade) LIKE LOWER(%s)"
                term = f"%{name}%"
                params = [term, term]

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            results = []
            has_coords = lat is not None and lng is not None

            for r in rows:
                bid = r['id']
                lat_b = lng_b = None
                try:
                    if r.get('latitude') is not None:
                        lat_b = float(r['latitude'])
                    if r.get('longitude') is not None:
                        lng_b = float(r['longitude'])
                except (TypeError, ValueError):
                    pass

                dist = None
                if has_coords and lat_b is not None and lng_b is not None:
                    dist = self._calculate_distance(float(lat), float(lng), lat_b, lng_b)

                if name:
                    include = True
                elif has_coords:
                    include = dist is not None and dist <= float(radius)
                else:
                    include = True

                if not include:
                    continue

                item = serialize_barbearia_for_template(cursor, r, bid, fetch_barbearia_opening_hours)
                item['id'] = str(bid)
                item['distance'] = dist
                item['place_id'] = f"db_{bid}"
                item['appointment_count'] = int(r.get('appointment_count') or 0)
                results.append(item)

            if name is None and lat is None and lng is None:
                results.sort(key=lambda x: x.get('appointment_count', 0), reverse=True)
            elif lat is not None and lng is not None:
                results.sort(
                    key=lambda x: (
                        x.get('distance') if x.get('distance') is not None else float('inf'),
                        -x.get('appointment_count', 0),
                    )
                )

            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"[ERRO] find_nearby_barbearias: {e}")
            import traceback
            traceback.print_exc()
            try:
                conn.close()
            except Exception:
                pass
            raise

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

# --- ROTAS PARA PÁGINAS HTML ---
@app.route('/confirmar-email')
def confirmar_email_page():
    """Renderiza a página de confirmação de email."""
    return render_template('ConfirmarEmail.html')

@app.route('/redefinir-senha')
def redefinir_senha_page():
    """Renderiza a página de redefinição de senha."""
    return render_template('RedefinirSenha.html')

@app.route('/cadastro-cliente')
def cadastro_cliente_page():
    """Renderiza a página de cadastro de cliente."""
    return render_template('CadastroCliente.html')

@app.route('/cadastro-barbearia')
def cadastro_barbearia_page():
    """Renderiza a página de cadastro de barbearia."""
    return render_template('CadastroBarbearia.html')

@app.route('/login')
def login_page():
    """Renderiza a página de login."""
    return render_template('Login.html')

@app.route('/tela-inicial')
def tela_inicial_page():
    """Página inicial da aplicação (mesmo conteúdo da landing)."""
    return render_template('index.html')

@app.route('/visualizar-barbearias')
def visualizar_barbearias_page():
    """Renderiza a página de visualização de barbearias."""
    return render_template('VisualizarBarbearias.html')

@app.route('/barbearia-detalhes/<int:barbearia_id>')
def barbearia_detalhes_page(barbearia_id):
    """Renderiza a página de detalhes de uma barbearia específica."""
    return render_template('BarbeariaDetalhes.html', barbearia_id=barbearia_id)

@app.route('/meus-agendamentos')
def meus_agendamentos_page():
    return render_template('MeusAgendamentos.html')

@app.route('/favoritos')
def favoritos_page():
    return render_template('Favoritos.html')

@app.route('/editar-perfil-barbearia')
def editar_perfil_barbearia_page():
    return render_template('EditarPerfilBarbearia.html')

@app.route('/editar-perfil-cliente')
def editar_perfil_cliente_page():
    return render_template('EditarPerfilCliente.html')

@app.route('/barbearia-dashboard')
def barbearia_dashboard_page():
    return render_template('BarbeariaDashboard.html')

@app.route('/cliente-dashboard')
def cliente_dashboard_page():
    return render_template('ClienteDashboard.html')

@app.route('/agendamentos-barbearia')
def agendamentos_barbearia_page():
    return render_template('AgendamentosBarbearia.html')

@app.route('/horarios-barbearia')
def horarios_barbearia_page():
    return render_template('HorariosBarbearia.html')

@app.route('/servicos-barbearia')
def servicos_barbearia_page():
    return render_template('ServicosBarbearia.html')

@app.route('/avaliacoes-barbearia')
def avaliacoes_barbearia_page():
    return render_template('AvaliacoesBarbearia.html')

@app.route('/termos-de-uso')
def termos_de_uso_page():
    return render_template('TermosDeUso.html')

# --- ROTAS DE BARBEARIA (Antiga barbearias_api.py) ---
@app.route('/api/barbearias/nearby', methods=['POST'])
def get_nearby_barbearias():
    data = request.get_json(silent=True) or {}
    lat = data.get('latitude')
    lng = data.get('longitude')
    name = (data.get('name') or '').strip() or None
    try:
        radius = float(data.get('radius', 5.0))
    except (TypeError, ValueError):
        radius = 5.0

    try:
        results = barbearias_service.find_nearby_barbearias(lat, lng, radius, name=name)
    except Exception as e:
        print(f"[ERRO] get_nearby_barbearias: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar barbearias. Tente novamente em instantes.',
            'barbearias': [],
            'total': 0,
        }), 500

    if results is None:
        return jsonify({
            'success': False,
            'message': 'Erro de conexão com o banco de dados. Verifique as variáveis MYSQL_* no Render.',
            'barbearias': [],
            'total': 0,
        }), 503

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
        if user.get('foto_perfil'):
            user['foto'] = user['foto_perfil']
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'message': 'Credenciais inválidas'}), 401

# --- Cliente: perfil (GET/PUT) e senha — o front usa localStorage (sem JWT); id na URL identifica o recurso ---
@app.route('/api/clientes/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco.'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nome_completo, email, telefone, foto_perfil FROM clientes WHERE id = %s', (cliente_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'Cliente não encontrado.'}), 404
    return jsonify({'success': True, 'cliente': row})

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco.'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, email, senha_hash FROM clientes WHERE id = %s', (cliente_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Cliente não encontrado.'}), 404
    new_email = data.get('email')
    if new_email and new_email != row['email']:
        cursor.execute('SELECT id FROM clientes WHERE email = %s AND id != %s', (new_email, cliente_id))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Este e-mail já está em uso.'}), 400
    updates = []
    params = []
    if 'nome_completo' in data:
        updates.append('nome_completo = %s')
        params.append(data['nome_completo'])
    if new_email is not None:
        updates.append('email = %s')
        params.append(new_email)
    if 'telefone' in data:
        updates.append('telefone = %s')
        params.append(data['telefone'])
    if 'foto_perfil' in data and data['foto_perfil']:
        updates.append('foto_perfil = %s')
        params.append(data['foto_perfil'])
    if not updates:
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Nada para atualizar.'})
    params.append(cliente_id)
    try:
        cursor.execute(f"UPDATE clientes SET {', '.join(updates)} WHERE id = %s", tuple(params))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Perfil atualizado.'})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/clientes/<int:cliente_id>/change-password', methods=['PUT'])
def change_password_cliente(cliente_id):
    data = request.get_json() or {}
    atual = data.get('senha_atual')
    nova = data.get('nova_senha')
    if not atual or not nova:
        return jsonify({'success': False, 'message': 'Senha atual e nova senha são obrigatórias.'}), 400
    if len(nova) < 8:
        return jsonify({'success': False, 'message': 'A nova senha deve ter pelo menos 8 caracteres.'}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco.'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, senha_hash FROM clientes WHERE id = %s', (cliente_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Cliente não encontrado.'}), 404
    if row['senha_hash'] != atual:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Senha atual incorreta.'}), 401
    cursor.execute('UPDATE clientes SET senha_hash = %s WHERE id = %s', (nova, cliente_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Senha alterada.'})

_BARBEARIA_PUT_FIELDS = frozenset({
    'nome_barbearia', 'nome_responsavel', 'email', 'foto_perfil', 'whatsapp', 'telefone_fixo',
    'instagram', 'facebook', 'website', 'descricao', 'cep', 'logradouro', 'numero',
    'complemento', 'bairro', 'cidade', 'estado', 'ponto_referencia', 'latitude', 'longitude',
    'quantidade_barbeiros',
})
_LOCATION_KEYS = frozenset({'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'complemento', 'ponto_referencia'})

@app.route('/api/barbearias/<int:barbearia_id>/fotos/<int:foto_id>', methods=['DELETE'])
def delete_barbearia_foto(barbearia_id, foto_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro DB'}), 500
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM barbearia_fotos WHERE id = %s AND barbearia_id = %s',
        (foto_id, barbearia_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()
    if not deleted:
        return jsonify({'success': False, 'message': 'Foto não encontrada.'}), 404
    return jsonify({'success': True})

@app.route('/api/barbearias/<int:barbearia_id>/fotos', methods=['GET'])
def list_barbearia_fotos(barbearia_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro DB'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, foto FROM barbearia_fotos WHERE barbearia_id = %s ORDER BY id',
        (barbearia_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'fotos': rows})

@app.route('/api/barbearias/<int:barbearia_id>/fotos', methods=['POST'])
def add_barbearia_foto(barbearia_id):
    data = request.get_json() or {}
    foto_b64 = data.get('foto')
    if not foto_b64:
        return jsonify({'success': False, 'message': 'Campo foto é obrigatório.'}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro DB'}), 500
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM barbearias WHERE id = %s', (barbearia_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Barbearia não encontrada.'}), 404
    try:
        cursor.execute(
            'INSERT INTO barbearia_fotos (barbearia_id, foto) VALUES (%s, %s)',
            (barbearia_id, foto_b64)
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/barbearias/<int:barbearia_id>', methods=['GET'])
def get_barbearia_details(barbearia_id):
    conn = get_db_connection()
    if not conn: return jsonify({'success': False, 'message': 'Erro DB'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM barbearias WHERE id = %s', (barbearia_id,))
    barbearia = cursor.fetchone()
    if barbearia:
        cursor.execute("SELECT * FROM servicos WHERE barbearia_id = %s AND status = 'ativo'", (barbearia_id,))
        servicos_detalhados = cursor.fetchall()
        barbearia = serialize_barbearia_for_template(cursor, barbearia, barbearia_id, fetch_barbearia_opening_hours)
        barbearia['servicos_detalhados'] = servicos_detalhados
    cursor.close(); conn.close()
    return jsonify({'success': True, 'barbearia': barbearia}) if barbearia else (jsonify({'success': False, 'message': 'Não encontrado.'}), 404)

@app.route('/api/barbearias/<int:barbearia_id>', methods=['PUT'])
def update_barbearia(barbearia_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco.'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM barbearias WHERE id = %s', (barbearia_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Barbearia não encontrada.'}), 404
    
    new_email = data.get('email')
    if new_email and new_email != row['email']:
        cursor.execute('SELECT id FROM barbearias WHERE email = %s AND id != %s', (new_email, barbearia_id))
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({'success': False, 'message': 'Este e-mail já está em uso por outra barbearia.'}), 400

    merged = dict(row)
    for k, v in data.items():
        if k in _BARBEARIA_PUT_FIELDS:
            merged[k] = v
    if _LOCATION_KEYS & set(data.keys()):
        lat, lng = _geocode_address(merged)
        if lat is not None and lng is not None:
            data['latitude'] = lat
            data['longitude'] = lng
    updates = []
    params = []
    for k, v in data.items():
        if k in _BARBEARIA_PUT_FIELDS and v is not None:
            updates.append(f'{k} = %s')
            params.append(v)
    if not updates:
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Nada para atualizar.'})
    params.append(barbearia_id)
    try:
        cursor.execute(f"UPDATE barbearias SET {', '.join(updates)} WHERE id = %s", tuple(params))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Dados atualizados.'})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/barbearias/<int:barbearia_id>/change-password', methods=['PUT'])
def change_password_barbearia(barbearia_id):
    """Endpoint exclusivo para alteração de senha da barbearia"""
    data = request.get_json() or {}
    atual = data.get('senha_atual')
    nova = data.get('nova_senha')

    if not atual or not nova:
        return jsonify({'success': False, 'message': 'Senha atual e nova senha são obrigatórias.'}), 400
    
    if len(nova) < 8:
        return jsonify({'success': False, 'message': 'A nova senha deve ter pelo menos 8 caracteres.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco.'}), 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT senha_hash FROM barbearias WHERE id = %s', (barbearia_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Barbearia não encontrada.'}), 404
        if row['senha_hash'] != atual:
            return jsonify({'success': False, 'message': 'A senha atual está incorreta.'}), 401
        
        cursor.execute('UPDATE barbearias SET senha_hash = %s WHERE id = %s', (nova, barbearia_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao processar: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- ROTAS DE SERVIÇOS ---
@app.route('/api/barbearias/<int:barbearia_id>/servicos', methods=['GET'])
def list_servicos_barbearia(barbearia_id):
    conn = get_db_connection()
    if not conn: return jsonify({'success': False}), 500
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM servicos WHERE barbearia_id = %s", (barbearia_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    servicos = [{
        "id": r["id"], "name": r["nome_servico"], "price": float(r["preco"] or 0),
        "duration": int(r["duracao_minutos"] or 30), "category": r.get("categoria") or "",
        "description": r.get("descricao") or "", "status": servico_db_status_to_api(r.get("status"))
    } for r in rows]
    return jsonify({'success': True, 'servicos': servicos})

@app.route('/api/barbearias/<int:barbearia_id>/servicos', methods=['POST'])
def create_servico_barbearia(barbearia_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO servicos (barbearia_id, nome_servico, preco, duracao_minutos, categoria, descricao, status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (barbearia_id, data.get("name"), data.get("price"), data.get("duration"), 
                     data.get("category"), data.get("description"), servico_api_status_to_db(data.get("status"))))
        conn.commit(); nid = cur.lastrowid
        return jsonify({'success': True, 'id': nid})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cur.close(); conn.close()

# --- ROTAS DE HORÁRIOS ---
@app.route('/api/barbearias/<int:barbearia_id>/horarios', methods=['GET'])
def get_horarios_barbearia(barbearia_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT dia_semana, status FROM horarios_status WHERE barbearia_id = %s", (barbearia_id,))
    status_map = {r["dia_semana"]: r["status"] for r in cur.fetchall()}
    cur.execute("SELECT id, dia_semana, inicio, fim FROM horarios_slots WHERE barbearia_id = %s", (barbearia_id,))
    slots_rows = cur.fetchall()
    cur.close(); conn.close()
    schedule = {day: {"status": status_map.get(day, "closed"), "slots": []} 
                for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}
    for r in slots_rows:
        if r["dia_semana"] in schedule:
            schedule[r["dia_semana"]]["slots"].append({"id": r["id"], "start": _as_hhmm(r["inicio"]), "end": _as_hhmm(r["fim"])})
    return jsonify({'success': True, 'schedule': schedule})

@app.route('/api/barbearias/<int:barbearia_id>/horarios', methods=['POST'])
def post_horarios_barbearia(barbearia_id):
    data = request.get_json() or {}
    schedule = data.get("schedule") or {}
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM horarios_slots WHERE barbearia_id = %s", (barbearia_id,))
        cur.execute("DELETE FROM horarios_status WHERE barbearia_id = %s", (barbearia_id,))
        for day, block in schedule.items():
            st = block.get("status", "closed")
            cur.execute("INSERT INTO horarios_status (barbearia_id, dia_semana, status) VALUES (%s,%s,%s)", (barbearia_id, day, st))
            if st == "open":
                for slot in block.get("slots", []):
                    cur.execute("INSERT INTO horarios_slots (barbearia_id, dia_semana, inicio, fim) VALUES (%s,%s,%s,%s)",
                                (barbearia_id, day, slot.get("start"), slot.get("end")))
        conn.commit(); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cur.close(); conn.close()

# --- LOGICA DE DISPONIBILIDADE ---
@app.route('/api/barbearias/<int:barbearia_id>/availability', methods=['GET'])
def get_availability(barbearia_id: int):
    date_str = request.args.get("date") # Formato: YYYY-MM-DD
    try:
        duration = int(request.args.get("duration") or 30)
    except ValueError:
        duration = 30

    if not date_str:
        return jsonify({'success': False, 'message': 'Data obrigatória'}), 400

    logger.info(f"--- CONSULTA DISPONIBILIDADE: Barbearia {barbearia_id} | Data {date_str} | Duração Solicitada {duration}min ---")

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        now_br = datetime.utcnow() - timedelta(hours=3)
        if d < now_br.date():
            logger.info("Consulta para data passada ignorada.")
            return jsonify({'success': True, 'slots': []})

        conn = get_db_connection(); cur = conn.cursor(dictionary=True)
        
        # REGRA 1: Buscar Capacidade (Quantidade de Barbeiros)
        cur.execute("SELECT quantidade_barbeiros FROM barbearias WHERE id = %s", (barbearia_id,))
        b_info = cur.fetchone()
        capacity = int(b_info["quantidade_barbeiros"]) if b_info and b_info.get("quantidade_barbeiros") else 1
        logger.info(f"Capacidade detectada: {capacity} barbeiros simultâneos.")

        day_key = _weekday_key(d)
        cur.execute("SELECT status FROM horarios_status WHERE barbearia_id = %s AND dia_semana = %s", (barbearia_id, day_key))
        if (st := cur.fetchone()) and st['status'] == 'closed':
            logger.info(f"Barbearia fechada no dia: {day_key}")
            return jsonify({'success': True, 'slots': []})

        cur.execute("SELECT inicio, fim FROM horarios_slots WHERE barbearia_id = %s AND dia_semana = %s", (barbearia_id, day_key))
        ranges = cur.fetchall()

        # REGRA 2 & 3: Buscar Ocupação Real (usando duracao_total do agendamento)
        # Se duracao_total for NULL, usamos s.duracao_minutos como fallback
        cur.execute("""SELECT a.horario_inicio, COALESCE(a.duracao_total, s.duracao_minutos, 30) as duracao
                       FROM agendamentos a 
                       LEFT JOIN servicos s ON a.servico_id = s.id 
                       WHERE a.barbearia_id = %s AND a.data_agendamento = %s AND a.status != 'cancelado'""", (barbearia_id, date_str))
        
        busy_raw = cur.fetchall()
        busy = []
        for br in busy_raw:
            start_m = _time_to_minutes(_as_hhmm(br["horario_inicio"]))
            dur_m = int(br["duracao"])
            busy.append((start_m, start_m + dur_m))
        
        logger.info(f"Agendamentos existentes (minutos do dia): {busy}")

        slots_out = []
        now_mins = now_br.hour * 60 + now_br.minute
        
        # REGRA 4: Cálculo de Slots
        for rng in ranges:
            t = _time_to_minutes(_as_hhmm(rng["inicio"]))
            end_rng = _time_to_minutes(_as_hhmm(rng["fim"]))
            
            while t + duration <= end_rng:
                # Bloqueio de 2h de antecedência para hoje
                if d == now_br.date() and t < (now_mins + 120): # Antecedência 2h
                    t += 30; continue
                
                # Verificar quantos barbeiros estão ocupados em QUALQUER MOMENTO desta janela solicitada
                overlaps = len([b for b in busy if _intervals_overlap(t, t + duration, b[0], b[1])])
                
                if overlaps < capacity:
                    slots_out.append(_minutes_to_time(t))
                
                t += 30 # Incremento fixo da agenda (passo de 30 min)
        
        logger.info(f"Slots disponíveis encontrados: {len(slots_out)}")
        return jsonify({'success': True, 'slots': slots_out})
    except Exception as e:
        logger.error(f"Erro ao calcular disponibilidade: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
    finally: 
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

# --- ROTAS DE AGENDAMENTOS ---
@app.route('/api/agendamentos', methods=['POST'])
def create_agendamento():    
    data = request.get_json() or {}
    
    # Validação Básica
    req_fields = ["cliente_id", "barbearia_id", "servico_id", "data_agendamento", "horario_inicio"]
    if not all(k in data for k in req_fields):
        return jsonify({'success': False, 'message': 'Campos obrigatórios ausentes'}), 400

    # REGRA: Validação final de capacidade no Servidor para evitar Race Condition
    # Em um sistema real, aqui chamaríamos a mesma lógica de get_availability
    # Para simplificar e garantir segurança:
    logger.info(f"TENTATIVA DE AGENDAMENTO: Cliente {data['cliente_id']} na Barbearia {data['barbearia_id']}")
    
    dur_total = int(data.get("duracao_total", 30))
    
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO agendamentos (cliente_id, barbearia_id, servico_id, data_agendamento, 
                       horario_inicio, duracao_total, status, valor_total, observacoes)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (data["cliente_id"], data["barbearia_id"], data["servico_id"], data["data_agendamento"],
                     data["horario_inicio"], data.get("duracao_total", 30), "pendente", 
                     data.get("valor_total"), data.get("observacoes")))
        conn.commit()
        logger.info(f"Agendamento {cur.lastrowid} criado com sucesso.")
        return jsonify({'success': True, 'id': cur.lastrowid, 'message': 'Agendamento realizado com sucesso!'})
    except Exception as e: 
        logger.error(f"Erro ao salvar agendamento: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
    finally: cur.close(); conn.close()

@app.route('/api/clientes/<int:cliente_id>/agendamentos', methods=['GET'])
def list_agendamentos_cliente(cliente_id):
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT a.*, b.nome_barbearia, s.nome_servico, s.duracao_minutos FROM agendamentos a
                   JOIN barbearias b ON b.id = a.barbearia_id JOIN servicos s ON s.id = a.servico_id
                   WHERE a.cliente_id = %s ORDER BY a.data_agendamento DESC""", (cliente_id,))
    rows = cur.fetchall(); cur.close(); conn.close()
    out = [{
        "id": r["id"], "barbearia": r["nome_barbearia"], "service": r["nome_servico"],
        "date": str(r["data_agendamento"]), "time": _as_hhmm(r["horario_inicio"]),
        "status": db_status_to_api(r["status"]), "price": float(r["valor_total"] or 0)
    } for r in rows]
    return jsonify({'success': True, 'agendamentos': out})

@app.route('/api/barbearias/<int:barbearia_id>/agendamentos', methods=['GET'])
def list_agendamentos_barbearia(barbearia_id):
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT a.*, c.nome_completo, c.telefone, s.nome_servico, s.preco FROM agendamentos a
                   JOIN clientes c ON c.id = a.cliente_id
                   JOIN servicos s ON s.id = a.servico_id
                   WHERE a.barbearia_id = %s
                   ORDER BY a.data_agendamento DESC""", (barbearia_id,))
    rows = cur.fetchall(); cur.close(); conn.close()
    out = [{
        "id": r["id"], "clientName": r["nome_completo"], "clientPhone": r["telefone"], "barbearia_id": r["barbearia_id"],
        "date": str(r["data_agendamento"]), "time": _as_hhmm(r["horario_inicio"]), "service": r["nome_servico"],
        "status": db_status_to_api(r["status"]), "totalPrice": float(r["valor_total"] or 0),
        "notes": r["observacoes"] # Adicionado para a lista completa de serviços
    } for r in rows]
    return jsonify({'success': True, 'agendamentos': out})

@app.route('/api/agendamentos/<int:agendamento_id>', methods=['PUT'])
def update_agendamento(agendamento_id):
    data = request.get_json() or {}
    conn = get_db_connection(); cur = conn.cursor()
    try:
        if 'status' in data:
            cur.execute("UPDATE agendamentos SET status = %s WHERE id = %s", (api_status_to_db(data['status']), agendamento_id))
            conn.commit()
        return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cur.close(); conn.close()

# --- AVALIAÇÕES E FAVORITOS ---
@app.route('/api/agendamentos/<int:agendamento_id>/avaliacao', methods=['POST'])
def post_avaliacao(agendamento_id):
    data = request.get_json() or {}
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("UPDATE agendamentos SET avaliacao_nota = %s, avaliacao_comentario = %s WHERE id = %s",
                    (data.get('rating'), data.get('comment'), agendamento_id))
        conn.commit(); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cur.close(); conn.close()

@app.route('/api/barbearias/<int:barbearia_id>/avaliacoes', methods=['GET'])
def list_avaliacoes(barbearia_id):
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT a.*, c.nome_completo as nome_cliente, s.nome_servico FROM agendamentos a
                   JOIN clientes c ON c.id = a.cliente_id JOIN servicos s ON s.id = a.servico_id
                   WHERE a.barbearia_id = %s AND a.avaliacao_nota IS NOT NULL""", (barbearia_id,))
    reviews = [_serialize_review_row(r, True) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify({'success': True, 'reviews': reviews})

@app.route('/api/clientes/<int:cliente_id>/favoritos', methods=['GET'])
def list_favoritos(cliente_id):
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT b.* FROM cliente_favoritos f JOIN barbearias b ON b.id = f.barbearia_id
                   WHERE f.cliente_id = %s""", (cliente_id,))
    rows = cur.fetchall()
    favoritos = []
    for r in rows:
        bid = r['id']
        cur.execute("SELECT nome_servico FROM servicos WHERE barbearia_id = %s AND status = 'ativo' LIMIT 3", (bid,))
        svcs = [s['nome_servico'] if isinstance(s, dict) else s[0] for s in cur.fetchall()]
        favoritos.append({
            "id": str(bid), "name": r["nome_barbearia"], "address": format_barbearia_address(r),
            "rating": 4.5, "phone": r["whatsapp"], "services": svcs
        })
    cur.close(); conn.close()
    return jsonify({'success': True, 'favoritos': favoritos})

@app.route('/api/clientes/<int:cliente_id>/favoritos', methods=['POST'])
def add_favorito(cliente_id):
    data = request.get_json() or {}
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT IGNORE INTO cliente_favoritos (cliente_id, barbearia_id) VALUES (%s,%s)", (cliente_id, data.get('barbearia_id')))
        conn.commit(); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cur.close(); conn.close()

@app.route('/api/clientes/<int:cliente_id>/favoritos/<int:barbearia_id>', methods=['DELETE'])
def remove_favorito(cliente_id, barbearia_id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM cliente_favoritos WHERE cliente_id = %s AND barbearia_id = %s", (cliente_id, barbearia_id))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'success': True})

# --- REGISTRO E ATUALIZAÇÃO ---
@app.route('/api/clientes', methods=['POST'])
def register_client():
    data = request.get_json()
    nome = str(data.get('nomeCompleto', '')).strip()
    if len(nome) < 3:
        return jsonify({'success': False, 'message': 'O nome deve ter pelo menos 3 caracteres.'}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 500
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome_completo, email, telefone, senha_hash) VALUES (%s, %s, %s, %s)",
                       (data.get('nomeCompleto'), data.get('email'), data.get('telefone'), data.get('senha')))
        conn.commit(); return jsonify({'success': True})
    except Exception as e: return jsonify({'success': False, 'message': str(e)}), 400
    finally: cursor.close(); conn.close()

@app.route('/api/barbearias', methods=['POST'])
def register_barbearia():
    data = request.get_json(silent=True)
    nb = str(data.get('nomeBarbearia', '')).strip()
    resp = str(data.get('responsavel', '')).strip()
    
    if len(nb) < 3 or len(resp) < 3:
        return jsonify({'success': False, 'message': 'O nome deve ter pelo menos 3 caracteres.'}), 400

    if not data:
        return jsonify({'success': False, 'message': 'Dados inválidos ou ausentes.'}), 400

    required = ('nomeBarbearia', 'cnpjCpf', 'responsavel', 'whatsapp', 'email', 'senha')
    missing = [f for f in required if not (data.get(f) or '').strip()]
    if missing:
        return jsonify({'success': False, 'message': 'Preencha todos os campos obrigatórios.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados.'}), 503

    lat, lng = _geocode_address(data)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO barbearias (
                   nome_barbearia, email, whatsapp, senha_hash, cnpj_cpf,
                   nome_responsavel, latitude, longitude, termos_aceitos
               ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)""",
            (
                data.get('nomeBarbearia').strip(),
                data.get('email').strip(),
                data.get('whatsapp').strip(),
                data.get('senha'),
                data.get('cnpjCpf').strip(),
                data.get('responsavel').strip(),
                lat,
                lng,
            ),
        )
        conn.commit()
        return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!'})
    except Exception as e:
        conn.rollback()
        err = str(e).lower()
        if 'duplicate' in err and 'email' in err:
            msg = 'Este e-mail já está cadastrado.'
        elif 'duplicate' in err and ('cnpj' in err or 'cpf' in err):
            msg = 'Este CPF/CNPJ já está cadastrado.'
        else:
            msg = str(e)
        return jsonify({'success': False, 'message': msg}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'message': 'API Unificada Online', 'timestamp': datetime.now().isoformat()})


@app.errorhandler(404)
def handle_not_found(e):
    """Evita resposta HTML em caminhos /api/... quando o front espera JSON."""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Recurso ou método não encontrado.'}), 404
    return e.get_response()

# Inicializa o banco ao carregar o módulo (necessário para Gunicorn/Render)
init_db()

if __name__ == '__main__':
    # O Railway define a porta automaticamente na variável PORT
    port = int(os.environ.get("PORT", 5000))
    # Debug False para produção
    app.run(debug=False, host='0.0.0.0', port=port)