#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Backend API para Barbearias
API para buscar e gerenciar barbearias próximas
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, replace
from datetime import datetime, time, timedelta, date
import os
import mysql.connector
from mysql.connector import Error
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Importar integração com Google Places
try:
    from .google_places_integration import PlacesService
except ImportError:
    from google_places_integration import PlacesService

app = Flask(__name__)
CORS(app)  # Permitir CORS para frontend

# Configuração do Banco de Dados MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # Usuário padrão do XAMPP
    'password': '',      # Senha padrão do XAMPP (geralmente vazia)
    'database': 'easycut_db', # Nome do banco que você criou no MySQL
    'charset': 'utf8mb4' # Garante suporte a acentos e emojis
}

def get_db_connection():
    """Cria conexão com o MySQL"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"[ERRO] Erro ao conectar no MySQL: {e}")
        return None

def init_db():
    """Inicializa o banco de dados"""
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            # Cria tabela de clientes se não existir (Sintaxe MySQL)
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
            
            # Cria tabela de barbearias se não existir
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
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # --- MIGRAÇÃO AUTOMÁTICA DE ESQUEMA ---
            # Verifica se as colunas novas existem, se não, adiciona (ALTER TABLE)
            cursor.execute("SHOW COLUMNS FROM barbearias")
            existing_columns = [col[0] for col in cursor.fetchall()]
            
            # Correção: Renomear descrição para descricao se necessário (compatibilidade)
            if 'descrição' in existing_columns and 'descricao' not in existing_columns:
                print("[MIGRAÇÃO] Renomeando coluna 'descrição' para 'descricao'...")
                cursor.execute("ALTER TABLE barbearias CHANGE COLUMN descrição descricao TEXT")
                existing_columns.append('descricao')
            
            columns_to_check = {
                'cnpj_cpf': 'VARCHAR(20)',
                'nome_responsavel': 'VARCHAR(255)',
                'whatsapp': 'VARCHAR(20)',
                'descricao': 'TEXT',
                'latitude': 'DECIMAL(10, 8)',
                'longitude': 'DECIMAL(11, 8)',
                'cep': 'VARCHAR(10)',
                'logradouro': 'VARCHAR(255)',
                'numero': 'VARCHAR(20)',
                'complemento': 'VARCHAR(255)',
                'bairro': 'VARCHAR(100)',
                'cidade': 'VARCHAR(100)',
                'estado': 'VARCHAR(2)',
                'ponto_referencia': 'VARCHAR(255)',
                'foto_perfil': 'LONGTEXT',
                'telefone_fixo': 'VARCHAR(20)',
                'website': 'VARCHAR(255)'
            }
            
            for col, dtype in columns_to_check.items():
                if col not in existing_columns:
                    print(f"[MIGRAÇÃO] Adicionando coluna '{col}' na tabela barbearias...")
                    cursor.execute(f"ALTER TABLE barbearias ADD COLUMN {col} {dtype}")

            # Cria tabela de servicos se não existir (coluna descricao sem acento para compatibilidade)
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
            # Migração: se a tabela tiver coluna "descrição", renomear para "descricao"
            cursor.execute("SHOW COLUMNS FROM servicos")
            servicos_cols = [c[0] for c in cursor.fetchall()]
            if 'descrição' in servicos_cols and 'descricao' not in servicos_cols:
                cursor.execute("ALTER TABLE servicos CHANGE COLUMN `descrição` descricao TEXT")

            # Cria tabela de agendamentos se não existir (observacoes sem acento)
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
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id),
                    FOREIGN KEY (servico_id) REFERENCES servicos(id)
                )
            ''')
            # Migração: renomear observações para observacoes se existir
            cursor.execute("SHOW COLUMNS FROM agendamentos")
            agend_cols = [c[0] for c in cursor.fetchall()]
            if 'observações' in agend_cols and 'observacoes' not in agend_cols:
                cursor.execute("ALTER TABLE agendamentos CHANGE COLUMN `observações` observacoes TEXT")

            # Cria tabela de status dos dias de funcionamento (Aberto/Fechado)
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

            # Cria tabela de slots de horário (Intervalos de tempo)
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

            # Cria tabela de fotos da galeria
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS barbearia_fotos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    barbearia_id INT NOT NULL,
                    foto LONGTEXT NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (barbearia_id) REFERENCES barbearias(id) ON DELETE CASCADE
                )
            ''')

            conn.commit()
            cursor.close()
            conn.close()
            print(f"[OK] Conectado ao MySQL (Banco: {DB_CONFIG['database']})")
    except Exception as e:
        print(f"[ERRO] Ao inicializar banco de dados: {e}")

def fetch_barbearia_opening_hours(cursor, barbearia_id):
    """Busca e formata os horários de funcionamento para exibição ao cliente"""
    try:
        # Fetch status
        cursor.execute('SELECT dia_semana, status FROM horarios_status WHERE barbearia_id = %s', (barbearia_id,))
        status_rows = cursor.fetchall()
        
        # Fetch slots (agregado: pega o início do primeiro slot e fim do último)
        cursor.execute('''
            SELECT dia_semana, MIN(inicio) as open_time, MAX(fim) as close_time 
            FROM horarios_slots 
            WHERE barbearia_id = %s 
            GROUP BY dia_semana
        ''', (barbearia_id,))
        slots_rows = cursor.fetchall()
        
        hours = {}
        # Mapear resultados
        status_map = {row['dia_semana']: row['status'] for row in status_rows}
        slots_map = {row['dia_semana']: row for row in slots_rows}
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            status = status_map.get(day, 'closed')
            if status == 'open' and day in slots_map:
                slot = slots_map[day]
                # Formatar hora para HH:MM
                open_t = str(slot['open_time'])[:5] if slot['open_time'] else "09:00"
                close_t = str(slot['close_time'])[:5] if slot['close_time'] else "18:00"
                hours[day] = {"open": open_t, "close": close_t}
            else:
                hours[day] = {"closed": True}
                
        return hours
    except Exception as e:
        print(f"[ERRO] Ao buscar horários para barbearia {barbearia_id}: {e}")
        return {}

@dataclass
class Barbearia:
    """Modelo de dados para barbearia"""
    id: str
    name: str
    address: str
    phone: Optional[str]
    email: Optional[str]
    latitude: float
    longitude: float
    rating: float
    price_level: int
    opening_hours: Dict[str, Any]
    services: List[str]
    photos: List[str]
    website: Optional[str]
    place_id: str
    distance: Optional[float] = None

@dataclass
class FilterOptions:
    """Opções de filtro para busca"""
    min_rating: Optional[float] = None
    max_price_level: Optional[int] = None
    services: Optional[List[str]] = None
    max_distance: Optional[float] = None

class BarbeariasService:
    """
    Serviço para gerenciar barbearias
    """
    
    def __init__(self):
        # Inicializar Google Places (opcional)
        self.places_service = None
        try:
            api_key = os.getenv('GOOGLE_PLACES_API_KEY')
            if api_key:
                self.places_service = PlacesService(api_key)
        except Exception as e:
            print(f"Google Places não disponível: {e}")
        
        # Dados mock removidos - usando apenas banco de dados
        # self.mock_barbearias = self._load_mock_data()
    
    def _load_mock_data(self) -> List[Barbearia]:
        """Carrega dados mock de barbearias"""
        return [
            Barbearia(
                id="1",
                name="Barber King",
                address="Rua das Flores, 123, Centro, Ipatinga - MG",
                phone="(31) 99999-9999",
                email="contato@barberking.com",
                latitude=-19.4708,
                longitude=-42.5489,
                rating=4.8,
                price_level=2,
                opening_hours={
                    "monday": {"open": "08:00", "close": "18:00"},
                    "tuesday": {"open": "08:00", "close": "18:00"},
                    "wednesday": {"open": "08:00", "close": "18:00"},
                    "thursday": {"open": "08:00", "close": "18:00"},
                    "friday": {"open": "08:00", "close": "19:00"},
                    "saturday": {"open": "08:00", "close": "17:00"},
                    "sunday": {"open": "09:00", "close": "15:00"}
                },
                services=["Design de sobrancelhas", "Barboterapia", "Pigmentação", "Relaxamento", "Progressivas", "Limpeza de pele", "Massagem facial", "Toalha quente"],
                photos=["https://via.placeholder.com/300x200/3b82f6/ffffff?text=Barber+King"],
                website="https://barberking.com",
                place_id="mock_place_1"
            ),
            Barbearia(
                id="2",
                name="Barbearia do João",
                address="Av. Central, 456, Cariru, Ipatinga - MG",
                phone="(31) 88888-8888",
                email="joao@barbearia.com",
                latitude=-19.4750,
                longitude=-42.5500,
                rating=4.6,
                price_level=1,
                opening_hours={
                    "monday": {"open": "09:00", "close": "19:00"},
                    "tuesday": {"open": "09:00", "close": "19:00"},
                    "wednesday": {"open": "09:00", "close": "19:00"},
                    "thursday": {"open": "09:00", "close": "19:00"},
                    "friday": {"open": "09:00", "close": "20:00"},
                    "saturday": {"open": "08:00", "close": "18:00"},
                    "sunday": {"open": "10:00", "close": "16:00"}
                },
                services=["Corte masculino", "Barba", "Sobrancelha", "Relaxamento"],
                photos=["https://via.placeholder.com/300x200/10b981/ffffff?text=Barbearia+Joao"],
                website=None,
                place_id="mock_place_2"
            ),
            Barbearia(
                id="3",
                name="Studio Hair",
                address="Rua Principal, 789, Cidade Nova, Ipatinga - MG",
                phone="(31) 77777-7777",
                email="studio@hair.com",
                latitude=-19.4650,
                longitude=-42.5450,
                rating=4.9,
                price_level=3,
                opening_hours={
                    "monday": {"open": "08:30", "close": "17:30"},
                    "tuesday": {"open": "08:30", "close": "17:30"},
                    "wednesday": {"open": "08:30", "close": "17:30"},
                    "thursday": {"open": "08:30", "close": "17:30"},
                    "friday": {"open": "08:30", "close": "18:30"},
                    "saturday": {"open": "09:00", "close": "16:00"},
                    "sunday": {"closed": True}
                },
                services=["Corte", "Barba", "Design de sobrancelhas", "Massagem", "Tratamentos"],
                photos=["https://via.placeholder.com/300x200/8b5cf6/ffffff?text=Studio+Hair"],
                website="https://studiohair.com",
                place_id="mock_place_3"
            ),
            Barbearia(
                id="4",
                name="Barbearia Central",
                address="Rua Comercial, 321, Centro, Ipatinga - MG",
                phone="(31) 66666-6666",
                email="central@barbearia.com",
                latitude=-19.4720,
                longitude=-42.5520,
                rating=4.4,
                price_level=1,
                opening_hours={
                    "monday": {"open": "07:00", "close": "20:00"},
                    "tuesday": {"open": "07:00", "close": "20:00"},
                    "wednesday": {"open": "07:00", "close": "20:00"},
                    "thursday": {"open": "07:00", "close": "20:00"},
                    "friday": {"open": "07:00", "close": "21:00"},
                    "saturday": {"open": "08:00", "close": "19:00"},
                    "sunday": {"open": "09:00", "close": "17:00"}
                },
                services=["Corte masculino", "Barba", "Sobrancelha", "Relaxamento", "Progressivas"],
                photos=["https://via.placeholder.com/300x200/f59e0b/ffffff?text=Barbearia+Central"],
                website=None,
                place_id="mock_place_4"
            )
        ]
    
    def _find_db_barbearias(self, lat: Optional[float], lng: Optional[float], radius: float, filters: Optional[FilterOptions], name_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca barbearias do banco de dados e filtra por proximidade."""
        conn = get_db_connection()
        if not conn:
            print("[ERRO] Não foi possível conectar ao banco para buscar barbearias. Retornando lista vazia.")
            return []

        try:
            cursor = conn.cursor(dictionary=True)
            
            # --- LÓGICA DE BUSCA CORRIGIDA ---
            # Constrói a query dinamicamente para ser mais flexível
            base_sql = "SELECT * FROM barbearias"
            where_clauses = []
            params = []
            
            if name_query:
                print(f"[DEBUG] Modo de busca: POR NOME ('{name_query}') - Ignorando filtro de raio")
                name_query = name_query.strip()
                print(f"[DEBUG] name_query após strip: '{name_query}'")
                # Busca expandida: Nome da barbearia (principal), CEP, Bairro, Cidade ou Logradouro
                # Usando COALESCE para evitar problemas com NULLs
                where_clauses.append("""(
                    LOWER(COALESCE(nome_barbearia, '')) LIKE LOWER(%s) OR 
                    LOWER(COALESCE(cep, '')) LIKE LOWER(%s) OR 
                    LOWER(COALESCE(bairro, '')) LIKE LOWER(%s) OR 
                    LOWER(COALESCE(cidade, '')) LIKE LOWER(%s) OR
                    LOWER(COALESCE(logradouro, '')) LIKE LOWER(%s)
                )""")
                term = f"%{name_query}%"
                print(f"[DEBUG] Termo de busca (com %): '{term}'")
                params.extend([term, term, term, term, term])
                print(f"[DEBUG] Parâmetros SQL: {params}")
            
            # Só exige coordenadas se NÃO estiver buscando por nome
            # Se buscar por nome, queremos encontrar mesmo que não tenha endereço cadastrado ainda
            if lat is not None and lng is not None and not name_query:
                print(f"[DEBUG] Modo de busca: POR LOCALIZAÇÃO (Lat: {lat}, Lng: {lng}, Raio: {radius}km)")
                where_clauses.append("latitude IS NOT NULL AND longitude IS NOT NULL")

            sql = base_sql
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            else:
                # Se não há cláusulas WHERE, buscar todas as barbearias (caso raro)
                print(f"[DEBUG] AVISO: Nenhuma cláusula WHERE foi adicionada. Buscando todas as barbearias.")

            print(f"[DEBUG] SQL final: {sql}")
            print(f"[DEBUG] Parâmetros finais: {params}")
            print(f"[DEBUG] Tipo dos parâmetros: {[type(p).__name__ for p in params]}")
            
            cursor.execute(sql, tuple(params))
            all_barbearias_db = cursor.fetchall()
            print(f"[DEBUG] Resultados do banco: {len(all_barbearias_db)}")
            if all_barbearias_db:
                print(f"[DEBUG] Primeira barbearia encontrada: {all_barbearias_db[0].get('nome_barbearia', 'N/A')}")
            else:
                print(f"[DEBUG] Nenhuma barbearia encontrada no banco de dados com os critérios fornecidos.")
            
            barbearias_with_distance = []
            for barbearia_db in all_barbearias_db:
                distance = None
                # Verifica se tem coordenadas antes de calcular distância
                if lat is not None and lng is not None and barbearia_db['latitude'] is not None and barbearia_db['longitude'] is not None:
                    distance = self._calculate_distance(lat, lng, float(barbearia_db['latitude']), float(barbearia_db['longitude']))
                
                # Se tem nome, inclui independente da distância (ou se estiver dentro do raio se location for fornecida)
                # Se não tem nome, obrigatoriamente filtra pelo raio
                if name_query or (distance is not None and distance <= radius):
                    # Buscar serviços
                    cursor.execute('SELECT nome_servico FROM servicos WHERE barbearia_id = %s', (barbearia_db['id'],))
                    servicos_db = cursor.fetchall()
                    
                    # Buscar horários reais
                    opening_hours = fetch_barbearia_opening_hours(cursor, barbearia_db['id'])
                    
                    # Formatar endereço
                    address_parts = []
                    if barbearia_db.get('logradouro'):
                        addr = barbearia_db['logradouro']
                        if barbearia_db.get('numero'):
                            addr += f", {barbearia_db['numero']}"
                        address_parts.append(addr)
                    if barbearia_db.get('bairro'):
                        address_parts.append(barbearia_db['bairro'])
                    if barbearia_db.get('cidade'):
                        city = barbearia_db['cidade']
                        if barbearia_db.get('estado'):
                            city += f" - {barbearia_db['estado']}"
                        address_parts.append(city)
                    address = ", ".join(address_parts) if address_parts else "Endereço não cadastrado"
                    
                    # Formatar para ser compatível com o frontend
                    formatted = {
                        "id": str(barbearia_db['id']),
                        "name": barbearia_db['nome_barbearia'],
                        "address": address,
                        "phone": barbearia_db.get('whatsapp') or barbearia_db.get('telefone_fixo') or '',
                        "email": barbearia_db.get('email') or '',
                        "latitude": float(barbearia_db['latitude']) if barbearia_db.get('latitude') is not None else None,
                        "longitude": float(barbearia_db['longitude']) if barbearia_db.get('longitude') is not None else None,
                        "rating": 5.0,  # Mock, pois não temos avaliações ainda
                        "price_level": 2, # Mock
                        "opening_hours": opening_hours,
                        "services": [s['nome_servico'] for s in servicos_db] if servicos_db else [],
                        "photos": [barbearia_db['foto_perfil']] if barbearia_db.get('foto_perfil') else [],
                        "website": barbearia_db.get('website') or None,
                        "place_id": f"db_{barbearia_db['id']}",
                        "distance": distance
                    }
                    # Armazenar como dict diretamente (será convertido para objeto Barbearia apenas se precisar aplicar filtros)
                    barbearias_with_distance.append(formatted)
            
            cursor.close()
            conn.close()

            # Aplicar filtros (precisa converter para objetos Barbearia temporariamente)
            if filters:
                barbearias_objects = [Barbearia(**b) if isinstance(b, dict) else b for b in barbearias_with_distance]
                filtered_objects = self._apply_filters(barbearias_objects, filters)
                # Converter de volta para dict
                barbearias_with_distance = [asdict(b) if not isinstance(b, dict) else b for b in filtered_objects]
            
            # Ordenar por distância (agora são dicts)
            # Se tiver distância, ordena por ela. Se não (busca só por nome sem gps), mantém ordem do banco ou alfabética
            barbearias_with_distance.sort(key=lambda x: (
                x.get('distance') if isinstance(x, dict) and x.get('distance') is not None else float('inf'),
                x.get('name', '') if isinstance(x, dict) else ''  # Desempate alfabético
            ))
            
            print(f"[DEBUG] Retornando {len(barbearias_with_distance)} barbearias do banco de dados")
            if barbearias_with_distance:
                print(f"[DEBUG] Primeira barbearia: {barbearias_with_distance[0].get('name', 'N/A')}")
            
            # Se o banco não retornou nada, retornar lista vazia (sem fallback para mock)
            if not barbearias_with_distance:
                if name_query:
                    print(f"[INFO] Nenhuma barbearia encontrada no banco com o nome '{name_query}'. Retornando lista vazia.")
                else:
                    print(f"[INFO] Nenhuma barbearia encontrada no banco de dados para a localização. Retornando lista vazia.")
                return []

            # Já são dicts, retornar diretamente
            return barbearias_with_distance
        except Exception as e:
            print(f"[ERRO] Erro ao buscar barbearias do banco: {e}")
            if conn and conn.is_connected():
                conn.close()
            return []  # Retornar lista vazia em caso de erro (sem fallback para mock)

    def find_nearby_barbearias(self, lat: Optional[float] = None, lng: Optional[float] = None, radius: float = 5.0, filters: Optional[FilterOptions] = None, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Encontra barbearias próximas com filtros
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            radius (float): Raio em km
            filters (FilterOptions, optional): Filtros aplicados
            name (str, optional): Nome da barbearia para busca
            
        Returns:
            List[Dict[str, Any]]: Lista de barbearias
        """
        print(f"[DEBUG] find_nearby_barbearias chamado: name='{name}', lat={lat}, lng={lng}, radius={radius}")
        # Prioriza a busca no banco de dados, que já tem fallback para mock.
        return self._find_db_barbearias(lat, lng, radius, filters, name)
    
    def _find_mock_barbearias(self, lat: Optional[float], lng: Optional[float], radius: float, filters: Optional[FilterOptions], name_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca barbearias usando dados mock - DESABILITADO: usando apenas banco de dados"""
        print(f"[DEBUG] Mock desabilitado. Retornando lista vazia.")
        return []  # Retornar lista vazia ao invés de dados mock
        
        # Código mock comentado - usando apenas banco de dados
        """
        print(f"[DEBUG] Buscando no Mock. Nome: '{name_query}', Lat: {lat}, Lng: {lng}")
        
        # Calcular distâncias e filtrar por raio
        barbearias_with_distance = []
        for barbearia in self.mock_barbearias:
            distance = None
            if lat is not None and lng is not None:
                distance = self._calculate_distance(lat, lng, barbearia.latitude, barbearia.longitude)
            
            # Lógica de filtro:
            # 1. Se tem busca por nome, verifica se bate com nome ou endereço
            # 2. Se não tem busca por nome, verifica raio de distância
            include = False
            if name_query:
                query = name_query.lower().strip()
                if query and (query in barbearia.name.lower() or query in barbearia.address.lower()):
                    include = True
            elif distance is not None and distance <= radius:
                include = True
            
            if include:
                # Criar cópia para não modificar o objeto original na lista mock
                b_copy = replace(barbearia)
                b_copy.distance = distance
                barbearias_with_distance.append(b_copy)
        
        # Aplicar filtros
        if filters:
            barbearias_with_distance = self._apply_filters(barbearias_with_distance, filters)
        
        # Ordenar por distância
        barbearias_with_distance.sort(key=lambda x: (
            x.distance if x.distance is not None else float('inf'),
            x.name
        ))
        
        # Converter para dict
        return [asdict(barbearia) for barbearia in barbearias_with_distance]
        """
    
    def _find_real_barbearias(self, lat: float, lng: float, radius: float, filters: Optional[FilterOptions]) -> List[Dict[str, Any]]:
        """Busca barbearias usando Google Places API"""
        try:
            # Converter km para metros
            radius_meters = int(radius * 1000)
            
            # Buscar barbearias próximas
            places_results = self.places_service.find_nearby_barbearias(lat, lng, radius_meters)
            
            barbearias = []
            for place in places_results:
                # Obter detalhes completos
                details = self.places_service.places_api.get_place_details(place['place_id'])
                if details:
                    barbearia = Barbearia(
                        id=details.place_id,
                        name=details.name,
                        address=details.formatted_address,
                        phone=None,  # Seria necessário buscar separadamente
                        email=None,
                        latitude=details.geometry['location']['lat'],
                        longitude=details.geometry['location']['lng'],
                        rating=details.rating or 0.0,
                        price_level=details.price_level or 0,
                        opening_hours={},  # Seria necessário buscar separadamente
                        services=[],  # Seria necessário buscar separadamente
                        photos=[],  # Seria necessário buscar separadamente
                        website=None,
                        place_id=details.place_id
                    )
                    
                    # Calcular distância
                    barbearia.distance = self._calculate_distance(lat, lng, barbearia.latitude, barbearia.longitude)
                    barbearias.append(barbearia)
            
            # Aplicar filtros
            if filters:
                barbearias = self._apply_filters(barbearias, filters)
            
            # Ordenar por distância
            barbearias.sort(key=lambda x: x.distance)
            
            return [asdict(barbearia) for barbearia in barbearias]
            
        except Exception as e:
            print(f"Erro ao buscar barbearias reais: {e}")
            return []  # Retornar lista vazia em caso de erro (sem fallback para mock)
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcula distância entre duas coordenadas em km"""
        import math
        
        R = 6371  # Raio da Terra em km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _apply_filters(self, barbearias: List[Barbearia], filters: FilterOptions) -> List[Barbearia]:
        """Aplica filtros às barbearias"""
        filtered = barbearias
        
        # Filtro por avaliação mínima
        if filters.min_rating is not None:
            filtered = [b for b in filtered if b.rating >= filters.min_rating]
        
        # Filtro por nível de preço máximo
        if filters.max_price_level is not None:
            filtered = [b for b in filtered if b.price_level <= filters.max_price_level]
        
        # Filtro por serviços
        if filters.services:
            filtered = [b for b in filtered if any(service in b.services for service in filters.services)]
        
        # Filtro por distância máxima
        if filters.max_distance is not None:
            filtered = [b for b in filtered if b.distance <= filters.max_distance]
        
        return filtered
    
    def get_barbearia_by_id(self, barbearia_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de uma barbearia específica do banco de dados"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(dictionary=True)
            if str(barbearia_id).isdigit():
                cursor.execute('SELECT * FROM barbearias WHERE id = %s', (barbearia_id,))
                barbearia_db = cursor.fetchone()
                
                if barbearia_db:
                    # Buscar serviços
                    cursor.execute('SELECT nome_servico FROM servicos WHERE barbearia_id = %s', (barbearia_id,))
                    servicos_db = cursor.fetchall()
                    
                    # Formatar endereço
                    address_parts = []
                    if barbearia_db.get('logradouro'):
                        addr = barbearia_db['logradouro']
                        if barbearia_db.get('numero'):
                            addr += f", {barbearia_db['numero']}"
                        address_parts.append(addr)
                    if barbearia_db.get('bairro'):
                        address_parts.append(barbearia_db['bairro'])
                    if barbearia_db.get('cidade'):
                        city = barbearia_db['cidade']
                        if barbearia_db.get('estado'):
                            city += f" - {barbearia_db['estado']}"
                        address_parts.append(city)
                    address = ", ".join(address_parts) if address_parts else "Endereço não cadastrado"
                    
                    return {
                        "id": str(barbearia_db['id']),
                        "name": barbearia_db['nome_barbearia'],
                        "address": address,
                        "phone": barbearia_db.get('whatsapp') or barbearia_db.get('telefone_fixo') or '',
                        "email": barbearia_db.get('email') or '',
                        "latitude": float(barbearia_db['latitude']) if barbearia_db.get('latitude') is not None else None,
                        "longitude": float(barbearia_db['longitude']) if barbearia_db.get('longitude') is not None else None,
                        "rating": 5.0,
                        "price_level": 2,
                        "opening_hours": {},
                        "services": [s['nome_servico'] for s in servicos_db] if servicos_db else [],
                        "photos": [barbearia_db['foto_perfil']] if barbearia_db.get('foto_perfil') else [],
                        "website": barbearia_db.get('website') or None,
                        "place_id": f"db_{barbearia_db['id']}"
                    }
            
            cursor.close()
            conn.close()
            return None
        except Exception as e:
            print(f"[ERRO] Erro ao buscar barbearia por ID: {e}")
            if conn and conn.is_connected():
                conn.close()
            return None

# Inicializar serviço
barbearias_service = BarbeariasService()

# Rotas da API
@app.route('/api/barbearias/nearby', methods=['POST'])
def get_nearby_barbearias():
    """Busca barbearias próximas"""
    try:
        data = request.get_json()
        
        # Validar dados: precisa de lat/lng OU nome
        # Tratamento robusto para evitar erros com strings vazias
        try:
            lat = data.get('latitude')
            if lat is not None and str(lat).strip() != "":
                lat = float(lat)
            else:
                lat = None
                
            lng = data.get('longitude')
            if lng is not None and str(lng).strip() != "":
                lng = float(lng)
            else:
                lng = None
        except (ValueError, TypeError):
            lat = None
            lng = None
            
        name = data.get('name')
        if name:
            name = str(name).strip()
            if name == "":
                name = None
        else:
            name = None
            
        print(f"[DEBUG] API Request recebida:")
        print(f"  - data completo: {data}")
        print(f"  - name (após processamento): '{name}'")
        print(f"  - lat: {lat}")
        print(f"  - lng: {lng}")

        # Validação: precisa ter nome OU localização
        if not name and (lat is None or lng is None):
            print(f"[DEBUG] Validação falhou: sem nome e sem localização")
            return jsonify({
                'success': False,
                'message': 'Forneça localização ou nome para busca',
                'barbearias': []
            }), 400
        
        print(f"[DEBUG] Validação passou. Buscando barbearias...")
        
        # Tratamento robusto para o raio
        try:
            radius_val = data.get('radius')
            radius = float(radius_val) if radius_val is not None and str(radius_val).strip() != "" else 5.0
        except (ValueError, TypeError):
            radius = 5.0
        
        # Criar filtros se fornecidos
        filters = None
        if 'filters' in data:
            filter_data = data['filters']
            filters = FilterOptions(
                min_rating=filter_data.get('min_rating'),
                max_price_level=filter_data.get('max_price_level'),
                services=filter_data.get('services'),
                max_distance=filter_data.get('max_distance')
            )
        
        # Buscar barbearias
        print(f"[DEBUG] Chamando find_nearby_barbearias com: name='{name}', lat={lat}, lng={lng}, radius={radius}")
        barbearias = barbearias_service.find_nearby_barbearias(lat, lng, radius, filters, name)
        print(f"[DEBUG] find_nearby_barbearias retornou {len(barbearias)} barbearias")
        if barbearias:
            first_barbearia = barbearias[0]
            if isinstance(first_barbearia, dict):
                print(f"[DEBUG] Primeira barbearia (dict): {first_barbearia.get('name', 'N/A')}")
            else:
                print(f"[DEBUG] Primeira barbearia (objeto): {first_barbearia.name if hasattr(first_barbearia, 'name') else 'N/A'}")
        
        # Converter objetos Barbearia para dict se necessário
        barbearias_dict = []
        for b in barbearias:
            if isinstance(b, dict):
                barbearias_dict.append(b)
            else:
                # Se for objeto Barbearia (dataclass), converter para dict usando asdict
                try:
                    barbearias_dict.append(asdict(b))
                except Exception as e:
                    print(f"[ERRO] Erro ao converter barbearia para dict: {e}")
                    # Fallback manual
                    barbearias_dict.append({
                        'id': str(b.id) if hasattr(b, 'id') else None,
                        'name': b.name if hasattr(b, 'name') else None,
                        'address': b.address if hasattr(b, 'address') else None,
                        'phone': b.phone if hasattr(b, 'phone') else None,
                        'email': b.email if hasattr(b, 'email') else None,
                        'latitude': b.latitude if hasattr(b, 'latitude') else None,
                        'longitude': b.longitude if hasattr(b, 'longitude') else None,
                        'rating': b.rating if hasattr(b, 'rating') else None,
                        'price_level': b.price_level if hasattr(b, 'price_level') else None,
                        'opening_hours': b.opening_hours if hasattr(b, 'opening_hours') else {},
                        'services': b.services if hasattr(b, 'services') else [],
                        'photos': b.photos if hasattr(b, 'photos') else [],
                        'website': b.website if hasattr(b, 'website') else None,
                        'place_id': b.place_id if hasattr(b, 'place_id') else None,
                        'distance': b.distance if hasattr(b, 'distance') else None
                    })
        
        print(f"[DEBUG] Convertido {len(barbearias_dict)} barbearias para dict")
        return jsonify({
            'success': True,
            'message': f'Encontradas {len(barbearias_dict)} barbearias',
            'barbearias': barbearias_dict,
            'total': len(barbearias_dict)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar barbearias: {str(e)}',
            'barbearias': []
        }), 500

@app.route('/api/barbearias/<barbearia_id>', methods=['GET'])
def get_barbearia_details(barbearia_id):
    """Obtém detalhes de uma barbearia específica do banco de dados"""
    try:
        # 1. Tentar buscar no banco de dados MySQL
        conn = get_db_connection()
        barbearia_db = None
        
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # Verificar se é ID numérico (banco)
                if str(barbearia_id).isdigit():
                    cursor.execute('SELECT * FROM barbearias WHERE id = %s', (barbearia_id,))
                    barbearia_db = cursor.fetchone()
                    
                    if barbearia_db:
                        # Buscar serviços
                        cursor.execute('SELECT * FROM servicos WHERE barbearia_id = %s', (barbearia_id,))
                        servicos_db = cursor.fetchall()

                        # Buscar fotos da galeria
                        cursor.execute('SELECT foto FROM barbearia_fotos WHERE barbearia_id = %s ORDER BY id DESC', (barbearia_id,))
                        fotos_db = cursor.fetchall()
                        
                        # Buscar horários reais
                        opening_hours = fetch_barbearia_opening_hours(cursor, barbearia_id)
                        
                        # Formatar resposta combinando dados do banco
                        # Converter tipos não serializáveis (Decimal, Datetime)
                        for key, val in barbearia_db.items():
                            if hasattr(val, 'to_eng_string'): # Decimal
                                barbearia_db[key] = float(val)
                            if isinstance(val, (datetime, time)): # Datetime/Time
                                barbearia_db[key] = str(val)
                        
                        # Adicionar campos compatíveis com o frontend existente
                        barbearia_db['name'] = barbearia_db['nome_barbearia']
                        
                        # Construir endereço completo
                        addr_parts = [
                            barbearia_db.get('logradouro'), 
                            barbearia_db.get('numero'), 
                            barbearia_db.get('bairro'), 
                            barbearia_db.get('cidade'), 
                            barbearia_db.get('estado')
                        ]
                        barbearia_db['address'] = ", ".join([str(p) for p in addr_parts if p])
                        
                        barbearia_db['phone'] = barbearia_db['whatsapp']
                        barbearia_db['services'] = [s['nome_servico'] for s in servicos_db] # Lista simples
                        
                        # Lista detalhada de serviços
                        barbearia_db['servicos_detalhados'] = []
                        for s in servicos_db:
                            if 'preco' in s and hasattr(s['preco'], 'to_eng_string'):
                                s['preco'] = float(s['preco'])
                            barbearia_db['servicos_detalhados'].append(s)

                        # Mock de dados faltantes (que ainda não estão no form de cadastro)
                        barbearia_db['rating'] = 5.0 
                        barbearia_db['price_level'] = 2
                        barbearia_db['opening_hours'] = opening_hours
                        
                        # Combinar foto de perfil com galeria
                        photos = [barbearia_db['foto_perfil']] if barbearia_db.get('foto_perfil') else []
                        photos.extend([f['foto'] for f in fotos_db])
                        barbearia_db['photos'] = photos
                        
                        cursor.close()
                        conn.close()
                        
                        return jsonify({
                            'success': True,
                            'message': 'Barbearia encontrada (DB)',
                            'barbearia': barbearia_db
                        })
                cursor.close()
                conn.close()
            except Exception as db_err:
                print(f"Erro ao buscar no banco: {db_err}")
                if conn.is_connected():
                    conn.close()

        # Se não encontrou no banco, retornar erro (sem fallback para mock)
        return jsonify({
            'success': False,
            'message': 'Barbearia não encontrada no banco de dados'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar barbearia: {str(e)}'
        }), 500

@app.route('/api/clientes/<int:cliente_id>', methods=['GET'])
def get_cliente_details(cliente_id):
    """Obtém detalhes de um cliente específico"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
        cliente = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente não encontrado'}), 404
            
        # Converter tipos
        for key, val in cliente.items():
            if isinstance(val, (datetime, time)):
                cliente[key] = str(val)
            
        return jsonify({
            'success': True,
            'cliente': cliente
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/barbearias/<int:barbearia_id>', methods=['PUT'])
def update_barbearia(barbearia_id):
    """Atualiza dados da barbearia"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500

        # --- LÓGICA DE GEOCODIFICAÇÃO AUTOMÁTICA ---
        address_fields_in_update = any(f in data for f in ['logradouro', 'numero', 'bairro', 'cidade', 'estado'])
        if address_fields_in_update:
            # Para construir o endereço completo, podemos precisar de partes existentes do DB
            cursor_check = conn.cursor(dictionary=True)
            cursor_check.execute('SELECT logradouro, numero, bairro, cidade, estado FROM barbearias WHERE id = %s', (barbearia_id,))
            current_address = cursor_check.fetchone() or {}
            cursor_check.close()

            # Constrói o endereço usando dados novos, com fallback para os dados atuais
            address_parts = [
                data.get('logradouro', current_address.get('logradouro')),
                data.get('numero', current_address.get('numero')),
                data.get('bairro', current_address.get('bairro')),
                data.get('cidade', current_address.get('cidade')),
                data.get('estado', current_address.get('estado')),
                'Brasil'
            ]
            full_address = ", ".join(filter(None, address_parts))

            if len(full_address.split(',')) > 2: # Checagem básica para não geocodificar apenas "Brasil"
                try:
                    geolocator = Nominatim(user_agent="easycut_app/1.0")
                    location = geolocator.geocode(full_address, timeout=10)
                    if location:
                        print(f"[INFO] Geocoding para '{full_address}' bem-sucedido: ({location.latitude}, {location.longitude})")
                        data['latitude'] = location.latitude
                        data['longitude'] = location.longitude
                    else:
                        print(f"[AVISO] Geocoding falhou para o endereço: {full_address}. Coordenadas não atualizadas.")
                except (GeocoderTimedOut, GeocoderUnavailable) as e:
                    print(f"[AVISO] Serviço de geocoding indisponível: {e}. Coordenadas não atualizadas.")
                except Exception as e:
                    print(f"[ERRO] Erro inesperado durante o geocoding: {e}")
        
        # Construir query dinâmica
        cursor = conn.cursor()
        fields = []
        values = []
        
        # Campos permitidos para atualização
        allowed_fields = [
            'nome_barbearia', 'nome_responsavel', 'whatsapp', 'telefone_fixo', 
            'instagram', 'facebook', 'website', 'descricao', 'cep', 
            'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'ponto_referencia',
            'foto_perfil', 'latitude', 'longitude'
        ]
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"`{field}` = %s")
                values.append(data[field])
                
        if not fields:
            conn.close()
            return jsonify({'success': False, 'message': 'Nenhum dado para atualizar'}), 400
            
        values.append(barbearia_id)
        sql = f"UPDATE barbearias SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(sql, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso'})
        
    except Exception as e:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    """Atualiza dados do cliente"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
            
        cursor = conn.cursor()
        
        fields = []
        values = []
        allowed_fields = ['nome_completo', 'telefone', 'foto_perfil', 'email']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])
                
        if not fields:
            return jsonify({'success': False, 'message': 'Nenhum dado para atualizar'}), 400
            
        values.append(cliente_id)
        sql = f"UPDATE clientes SET {', '.join(fields)} WHERE id = %s"
        
        cursor.execute(sql, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clientes', methods=['POST'])
def register_client():
    """Cadastra um novo cliente"""
    try:
        data = request.get_json()
        
        # Log para visualizar os dados chegando no terminal
        print(f"Recebendo cadastro de cliente: {data}")
        
        # Verificar se os campos essenciais vieram
        if not data.get('nomeCompleto') or not data.get('email') or not data.get('senha'):
            print("[ALERTA] Tentativa de cadastro com dados incompletos!")
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400

        # Salvar no banco de dados
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'}), 200
            
        cursor = conn.cursor()
        
        # Sintaxe MySQL usa %s em vez de ?
        sql = "INSERT INTO clientes (nome_completo, email, telefone, senha_hash, termos_aceitos) VALUES (%s, %s, %s, %s, %s)"
        val = (
            data.get('nomeCompleto'),
            data.get('email'),
            data.get('telefone'),
            data.get('senha'),
            1 # Termos aceitos (padrão ao cadastrar)
        )
        
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] Cliente salvo no banco de dados com sucesso!")
        
        return jsonify({
            'success': True,
            'message': 'Cadastro realizado com sucesso!'
        })
        
    except mysql.connector.Error as err:
        if err.errno == 1062: # Código de erro para duplicidade no MySQL
            return jsonify({
                'success': False,
                'message': 'Este email já está cadastrado.'
            }), 400
        elif err.errno == 1054: # Erro de coluna desconhecida
            print(f"[ERRO] Estrutura do banco incorreta: {err}")
            print("[SOLUÇÃO] A tabela 'clientes' tem colunas diferentes do esperado.")
            print("          Apague a tabela 'clientes' no seu banco de dados e reinicie o sistema.")
            return jsonify({
                'success': False, 
                'message': 'Erro interno: Estrutura do banco de dados desatualizada.'
            }), 500
        print(f"Erro MySQL: {err}")
        return jsonify({'success': False, 'message': f'Erro no banco: {str(err)}'}), 500
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/barbearias', methods=['POST'])
def register_barbearia():
    """Cadastra uma nova barbearia"""
    try:
        # Tentar obter JSON. Se falhar, tenta form data
        data = request.get_json(force=True, silent=True)
        if not data:
            data = request.form.to_dict()
        
        if not data:
            print("[ERRO] JSON inválido ou vazio recebido no cadastro de barbearia")
            return jsonify({'success': False, 'message': 'Dados inválidos ou vazios enviados pelo formulário'}), 200
        
        # Log para visualizar os dados chegando no terminal
        print(f"Recebendo cadastro de barbearia: {data}")
        print(f"Chaves recebidas: {list(data.keys())}")
        
        # Normalizar chaves (aceitar camelCase e snake_case)
        nome_barbearia = data.get('nomeBarbearia') or data.get('nome_barbearia') or data.get('nome')
        email = data.get('email')
        senha = data.get('senha') or data.get('senha_hash')
        cnpj_cpf = data.get('cnpjCpf') or data.get('cnpj_cpf') or data.get('cnpj') or data.get('cpf') or data.get('documento')
        responsavel = data.get('responsavel') or data.get('nome_responsavel') or data.get('nomeResponsavel')
        whatsapp = data.get('whatsapp') or data.get('telefone') or data.get('telefone_whatsapp') or data.get('celular') or data.get('tel')
        
        # Campos de endereço opcionais no cadastro
        cep = data.get('cep')
        logradouro = data.get('logradouro') or data.get('rua')
        numero = data.get('numero')
        bairro = data.get('bairro')
        cidade = data.get('cidade')
        estado = data.get('estado') or data.get('uf')
        
        # Verificar campos obrigatórios
        missing_fields = []
        if not nome_barbearia: missing_fields.append('Nome da Barbearia')
        if not email: missing_fields.append('Email')
        if not senha: missing_fields.append('Senha')
        if not cnpj_cpf: missing_fields.append('CNPJ/CPF')
        if not responsavel: missing_fields.append('Nome do Responsável')
        if not whatsapp: missing_fields.append('WhatsApp/Telefone')
            
        if missing_fields:
            print(f"[ALERTA] Campos faltando: {missing_fields}")
            return jsonify({'success': False, 'message': f'Preencha todos os campos obrigatórios: {", ".join(missing_fields)}'}), 400

        # Salvar no banco de dados
        conn = get_db_connection()
        if not conn:
            print("[ERRO] Falha ao conectar no banco de dados")
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados. Verifique se o MySQL está rodando.'}), 200
            
        # Tentar geocodificar se tiver endereço
        latitude, longitude = None, None
        if logradouro and cidade:
            latitude, longitude = _geocode_address(data)
            
        cursor = conn.cursor()
        
        # Query SQL
        sql = """
            INSERT INTO barbearias 
            (nome_barbearia, email, whatsapp, senha_hash, termos_aceitos, cnpj_cpf, nome_responsavel,
             cep, logradouro, numero, bairro, cidade, estado, latitude, longitude) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        val = (
            nome_barbearia,
            email,
            whatsapp,
            senha,
            1, # Termos aceitos
            cnpj_cpf,
            responsavel,
            cep,
            logradouro,
            numero,
            bairro,
            cidade,
            estado,
            latitude,
            longitude
        )
        
        cursor.execute(sql, val)
        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] Barbearia salva no banco de dados com sucesso!")
        
        return jsonify({
            'success': True,
            'message': 'Cadastro de barbearia realizado com sucesso!'
        })
        
    except mysql.connector.Error as err:
        print(f"Erro MySQL: {err}")
        if err.errno == 1062: # Código de erro para duplicidade no MySQL
            msg = str(err)
            if 'email' in msg:
                return jsonify({'success': False, 'message': 'Este email já está cadastrado.'}), 400
            if 'cnpj_cpf' in msg:
                return jsonify({'success': False, 'message': 'Este CNPJ/CPF já está cadastrado.'}), 400
            return jsonify({'success': False, 'message': 'Registro duplicado (Email ou CNPJ/CPF).'}), 400
            
        return jsonify({'success': False, 'message': f'Erro no banco de dados: {str(err)}'}), 500
        
    except Exception as e:
        print(f"Erro ao cadastrar barbearia: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro interno ao processar cadastro: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Realiza login do usuário"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('senha')
        
        print(f"Recebendo tentativa de login: {email}")
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        # 1. Tentar buscar em clientes
        cursor.execute('SELECT id, nome_completo, email, senha_hash, telefone, foto_perfil FROM clientes WHERE email = %s', (email,))
        user = cursor.fetchone()
        user_type = 'cliente'
        
        # 2. Se não achou em clientes, tentar em barbearias
        if not user:
            # Mapeando whatsapp como telefone para manter compatibilidade com o frontend
            cursor.execute('SELECT id, nome_barbearia, email, senha_hash, whatsapp as telefone, foto_perfil FROM barbearias WHERE email = %s', (email,))
            user = cursor.fetchone()
            user_type = 'barbearia'
        
        cursor.close()
        conn.close()
        
        if user and user['senha_hash'] == password:
            # Normalizar nome para resposta (clientes usam nome_completo, barbearias usam nome_barbearia)
            nome_exibicao = user.get('nome_completo') or user.get('nome_barbearia')
            
            print(f"Login sucesso: {nome_exibicao} ({user_type})")
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'user': {
                    'id': user['id'],
                    'nome': nome_exibicao,
                    'email': user['email'],
                    'telefone': user['telefone'],
                    'foto': user['foto_perfil'],
                    'tipo': user_type
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
            
    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@app.route('/api/clientes', methods=['GET'])
def list_clients():
    """Lista clientes cadastrados (para verificação)"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Erro de conexão'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nome_completo, email, telefone, data_criacao FROM clientes ORDER BY id DESC')
        clientes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'total': len(clientes),
            'clientes': clientes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- Serviços da barbearia (CRUD no banco) ----------
@app.route('/api/barbearias/<int:barbearia_id>/servicos', methods=['GET'])
def list_barbearia_servicos(barbearia_id):
    """Lista todos os serviços cadastrados da barbearia (pode ser vazio)."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT id, barbearia_id, nome_servico, preco, duracao_minutos, categoria, descricao, status
            FROM servicos
            WHERE barbearia_id = %s
            ORDER BY id ASC
        ''', (barbearia_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Normalizar para o frontend: name, price, duration, category, description, status (ativo/inativo)
        servicos = []
        for r in rows:
            servicos.append({
                'id': r['id'],
                'barbearia_id': r['barbearia_id'],
                'name': r['nome_servico'],
                'price': float(r['preco']) if r['preco'] is not None else 0,
                'duration': r['duracao_minutos'] or 0,
                'category': r['categoria'] or 'outros',
                'description': r['descricao'] or '',
                'status': 'active' if (r['status'] or '').lower() == 'ativo' else 'inactive',
            })
        return jsonify({'success': True, 'servicos': servicos})
    except Exception as e:
        print(f"Erro ao listar serviços: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/barbearias/<int:barbearia_id>/servicos', methods=['POST'])
def create_barbearia_servico(barbearia_id):
    """Cadastra um novo serviço para a barbearia (salva na tabela servicos)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados do serviço não enviados'}), 400
        nome_servico = data.get('name') or data.get('nome_servico')
        preco = data.get('price') or data.get('preco')
        duracao = data.get('duration') or data.get('duracao_minutos')
        categoria = data.get('category') or data.get('categoria') or None
        descricao = data.get('description') or data.get('descricao') or None
        status = (data.get('status') or 'active').lower()
        status_db = 'ativo' if status == 'active' else 'inativo'
        if not nome_servico:
            return jsonify({'success': False, 'message': 'Nome do serviço é obrigatório'}), 400
        if preco is None:
            return jsonify({'success': False, 'message': 'Preço é obrigatório'}), 400
        if duracao is None:
            return jsonify({'success': False, 'message': 'Duração é obrigatória'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'}), 500
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO servicos (barbearia_id, nome_servico, preco, duracao_minutos, categoria, descricao, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (barbearia_id, nome_servico, float(preco), int(duracao), categoria, descricao, status_db))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Serviço cadastrado com sucesso!',
            'id': new_id
        })
    except Exception as e:
        print(f"Erro ao cadastrar serviço: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/barbearias/<int:barbearia_id>/servicos/<int:servico_id>', methods=['PUT'])
def update_barbearia_servico(barbearia_id, servico_id):
    """Atualiza um serviço da barbearia."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não enviados'}), 400
        nome_servico = data.get('name') or data.get('nome_servico')
        preco = data.get('price') or data.get('preco')
        duracao = data.get('duration') or data.get('duracao_minutos')
        categoria = data.get('category') or data.get('categoria')
        descricao = data.get('description') or data.get('descricao')
        status = (data.get('status') or 'active').lower()
        status_db = 'ativo' if status == 'active' else 'inativo'
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE servicos SET nome_servico=%s, preco=%s, duracao_minutos=%s, categoria=%s, descricao=%s, status=%s
               WHERE id=%s AND barbearia_id=%s''',
            (nome_servico, float(preco), int(duracao), categoria, descricao, status_db, servico_id, barbearia_id)
        )
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'Serviço não encontrado'}), 404
        return jsonify({'success': True, 'message': 'Serviço atualizado com sucesso!'})
    except Exception as e:
        print(f"Erro ao atualizar serviço: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/barbearias/<int:barbearia_id>/servicos/<int:servico_id>', methods=['DELETE'])
def delete_barbearia_servico(barbearia_id, servico_id):
    """Remove um serviço da barbearia."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        cursor.execute('DELETE FROM servicos WHERE id = %s AND barbearia_id = %s', (servico_id, barbearia_id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'Serviço não encontrado'}), 404
        return jsonify({'success': True, 'message': 'Serviço excluído com sucesso!'})
    except Exception as e:
        print(f"Erro ao excluir serviço: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------- Agendamentos ----------
@app.route('/api/agendamentos', methods=['POST'])
def create_agendamento():
    """Cria um novo agendamento (cliente agenda na barbearia)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não enviados'}), 400
        cliente_id = data.get('cliente_id')
        barbearia_id = data.get('barbearia_id')
        servico_id = data.get('servico_id')
        data_agendamento = data.get('data_agendamento') or data.get('date')
        horario_inicio = data.get('horario_inicio') or data.get('time')
        valor_total = data.get('valor_total') or data.get('totalPrice')
        observacoes = data.get('observacoes') or data.get('observacoes') or ''
        if None in (cliente_id, barbearia_id, servico_id, data_agendamento, horario_inicio):
            return jsonify({'success': False, 'message': 'Preencha cliente, barbearia, serviço, data e horário'}), 400
        cliente_id = int(cliente_id)
        barbearia_id = int(barbearia_id)
        servico_id = int(servico_id)
        valor_total = float(valor_total) if valor_total is not None else None
        # horario_inicio pode vir "09:30" ou "09:30:00"
        if isinstance(horario_inicio, str) and len(horario_inicio) == 5:
            horario_inicio = horario_inicio + ':00'
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO agendamentos (cliente_id, barbearia_id, servico_id, data_agendamento, horario_inicio, status, valor_total, observacoes)
            VALUES (%s, %s, %s, %s, %s, 'pendente', %s, %s)
        ''', (cliente_id, barbearia_id, servico_id, data_agendamento, horario_inicio, valor_total, observacoes))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Agendamento realizado com sucesso!', 'id': new_id})
    except Exception as e:
        print(f"Erro ao criar agendamento: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


def _row_to_agendamento_dict(r, barbearia_nome=None, servico_nome=None):
    """Converte linha do agendamentos + joins para dict do frontend."""
    status = (r.get('status') or 'pendente').lower()
    status_front = {'pendente': 'pending', 'confirmado': 'confirmed', 'confirmada': 'confirmed',
                    'cancelado': 'cancelled', 'cancelada': 'cancelled', 'concluido': 'completed', 'concluída': 'completed'}
    status = status_front.get(status, status if status in ('pending', 'confirmed', 'cancelled', 'completed') else 'pending')
    horario = r.get('horario_inicio')
    if hasattr(horario, 'strftime'):
        horario = horario.strftime('%H:%M') if horario else ''
    else:
        horario = str(horario)[:5] if horario else ''
    data_ag = r.get('data_agendamento')
    data_str = str(data_ag) if data_ag else ''
    return {
        'id': str(r.get('id')),
        'barbearia': barbearia_nome or '',
        'barbearia_id': r.get('barbearia_id'),
        'service': servico_nome or '',
        'date': data_str,
        'time': horario,
        'status': status,
        'price': str(r.get('valor_total') or '0'),
        'duration': 0,  # opcional, pode vir do servico
        'notes': (r.get('observacoes') or '') or '',
        'rating': r.get('avaliacao_nota'),
        'cliente_id': r.get('cliente_id'),
        'servico_id': r.get('servico_id'),
    }


@app.route('/api/clientes/<int:cliente_id>/agendamentos', methods=['GET'])
def list_cliente_agendamentos(cliente_id):
    """Lista agendamentos do cliente (Meus Agendamentos)."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.id, a.cliente_id, a.barbearia_id, a.servico_id, a.data_agendamento, a.horario_inicio,
                   a.status, a.valor_total, a.observacoes, a.avaliacao_nota, a.avaliacao_comentario,
                   b.nome_barbearia AS barbearia_nome, s.nome_servico AS servico_nome
            FROM agendamentos a
            LEFT JOIN barbearias b ON b.id = a.barbearia_id
            LEFT JOIN servicos s ON s.id = a.servico_id
            WHERE a.cliente_id = %s
            ORDER BY a.data_agendamento DESC, a.horario_inicio DESC
        ''', (cliente_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        lista = [_row_to_agendamento_dict(r, r.get('barbearia_nome'), r.get('servico_nome')) for r in rows]
        return jsonify({'success': True, 'agendamentos': lista})
    except Exception as e:
        print(f"Erro ao listar agendamentos do cliente: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/barbearias/<int:barbearia_id>/agendamentos', methods=['GET'])
def list_barbearia_agendamentos(barbearia_id):
    """Lista agendamentos da barbearia."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT a.id, a.cliente_id, a.barbearia_id, a.servico_id, a.data_agendamento, a.horario_inicio,
                   a.status, a.valor_total, a.observacoes, a.avaliacao_nota,
                   b.nome_barbearia AS barbearia_nome, s.nome_servico AS servico_nome,
                   c.nome_completo AS cliente_nome, c.telefone AS cliente_telefone
            FROM agendamentos a
            LEFT JOIN barbearias b ON b.id = a.barbearia_id
            LEFT JOIN servicos s ON s.id = a.servico_id
            LEFT JOIN clientes c ON c.id = a.cliente_id
            WHERE a.barbearia_id = %s
            ORDER BY a.data_agendamento DESC, a.horario_inicio DESC
        ''', (barbearia_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # Para a barbearia: retornar formato com clientName, clientPhone, date, time, services, totalPrice, status
        lista = []
        for r in rows:
            status = (r.get('status') or 'pendente').lower()
            status_front = {'pendente': 'pending', 'confirmado': 'confirmed', 'confirmada': 'confirmed',
                           'cancelado': 'cancelled', 'cancelada': 'cancelled', 'concluido': 'completed', 'concluída': 'completed'}
            st = status_front.get(status, status)
            horario = r.get('horario_inicio')
            if hasattr(horario, 'strftime'):
                horario = horario.strftime('%H:%M') if horario else ''
            else:
                horario = str(horario)[:5] if horario else ''
            lista.append({
                'id': str(r.get('id')),
                'clientName': r.get('cliente_nome') or '',
                'clientPhone': r.get('cliente_telefone') or '',
                'date': str(r.get('data_agendamento') or ''),
                'time': horario,
                'services': [r.get('servico_nome') or ''] if r.get('servico_nome') else [],
                'totalPrice': float(r.get('valor_total') or 0),
                'status': st,
                'notes': (r.get('observacoes') or '') or '',
                'createdBy': 'cliente',
            })
        return jsonify({'success': True, 'agendamentos': lista})
    except Exception as e:
        print(f"Erro ao listar agendamentos da barbearia: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/agendamentos/<int:agendamento_id>', methods=['PUT'])
def update_agendamento_status(agendamento_id):
    """Atualiza status do agendamento (confirmar, cancelar, concluir)."""
    try:
        data = request.get_json() or {}
        status = (data.get('status') or '').strip().lower()
        status_db_map = {
            'pending': 'pendente', 'pendente': 'pendente',
            'confirmed': 'confirmado', 'confirmado': 'confirmado',
            'cancelled': 'cancelado', 'cancelado': 'cancelado',
            'completed': 'concluído', 'concluido': 'concluído', 'concluído': 'concluído',
        }
        status_db = status_db_map.get(status)
        if not status_db:
            return jsonify({'success': False, 'message': 'Status inválido'}), 400
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        cursor.execute('UPDATE agendamentos SET status = %s WHERE id = %s', (status_db, agendamento_id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            return jsonify({'success': False, 'message': 'Agendamento não encontrado'}), 404
        return jsonify({'success': True, 'message': 'Status atualizado com sucesso!'})
    except Exception as e:
        print(f"Erro ao atualizar agendamento: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ---------- Disponibilidade (Cálculo de Horários Livres) ----------
@app.route('/api/barbearias/<int:barbearia_id>/availability', methods=['GET'])
def get_barbearia_availability(barbearia_id):
    """Calcula horários disponíveis baseados na configuração e agendamentos"""
    try:
        date_str = request.args.get('date')
        # Duração do serviço desejado (padrão 30min se não informado)
        duration_min = int(request.args.get('duration', 30)) 
        
        if not date_str:
            return jsonify({'success': False, 'message': 'Data é obrigatória (YYYY-MM-DD)'}), 400
            
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 1. Descobrir dia da semana (monday, tuesday...)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = days[target_date.weekday()]
        
        conn = get_db_connection()
        if not conn: return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor(dictionary=True)
        
        # 2. Verificar se a barbearia abre nesse dia
        cursor.execute('SELECT status FROM horarios_status WHERE barbearia_id = %s AND dia_semana = %s', (barbearia_id, day_name))
        status_row = cursor.fetchone()
        
        if not status_row or status_row['status'] == 'closed':
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'slots': [], 'message': 'Fechado neste dia'})
            
        # 3. Buscar intervalos de funcionamento (ex: 09:00-12:00, 13:00-18:00)
        cursor.execute('SELECT inicio, fim FROM horarios_slots WHERE barbearia_id = %s AND dia_semana = %s ORDER BY inicio', (barbearia_id, day_name))
        working_slots = cursor.fetchall()
        
        # 4. Buscar agendamentos JÁ EXISTENTES nesse dia (exceto cancelados)
        # Precisamos da duração do serviço agendado para saber quando o horário libera
        cursor.execute('''
            SELECT a.horario_inicio, s.duracao_minutos 
            FROM agendamentos a
            JOIN servicos s ON a.servico_id = s.id
            WHERE a.barbearia_id = %s 
            AND a.data_agendamento = %s
            AND a.status != 'cancelado'
        ''', (barbearia_id, date_str))
        appointments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 5. Calcular slots livres (Matemática de horários)
        available_slots = []
        
        # Preparar lista de intervalos ocupados (Start, End)
        booked_intervals = []
        for appt in appointments:
            start = appt['horario_inicio']
            # Correção para MySQL Connector que retorna timedelta
            if isinstance(start, timedelta): start = (datetime.min + start).time()
            
            appt_start = datetime.combine(target_date, start)
            dur = appt['duracao_minutos'] or 30
            appt_end = appt_start + timedelta(minutes=dur)
            booked_intervals.append((appt_start, appt_end))
            
        # Iterar sobre cada intervalo de funcionamento da barbearia
        for slot in working_slots:
            start = slot['inicio']
            if isinstance(start, timedelta): start = (datetime.min + start).time()
            end = slot['fim']
            if isinstance(end, timedelta): end = (datetime.min + end).time()
            
            current = datetime.combine(target_date, start)
            limit = datetime.combine(target_date, end)
            
            # Gerar slots a cada 30 min dentro do horário de funcionamento
            while current + timedelta(minutes=duration_min) <= limit:
                slot_start = current
                slot_end = current + timedelta(minutes=duration_min)
                
                # Verificar colisão com agendamentos existentes
                is_blocked = False
                for b_start, b_end in booked_intervals:
                    # Se houver sobreposição: (StartA < EndB) e (EndA > StartB)
                    if slot_start < b_end and slot_end > b_start:
                        is_blocked = True
                        break
                
                if not is_blocked:
                    available_slots.append(slot_start.strftime('%H:%M'))
                
                # Avançar para o próximo horário (grade de 30 em 30 min)
                current += timedelta(minutes=30)
                
        return jsonify({'success': True, 'slots': available_slots})
        
    except Exception as e:
        print(f"Erro ao calcular disponibilidade: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ---------- Horários de Funcionamento ----------
@app.route('/api/barbearias/<int:barbearia_id>/horarios', methods=['GET'])
def get_horarios(barbearia_id):
    """Busca os horários de funcionamento da barbearia"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Buscar status dos dias
        cursor.execute('SELECT dia_semana, status FROM horarios_status WHERE barbearia_id = %s', (barbearia_id,))
        status_rows = cursor.fetchall()
        
        # Buscar slots
        cursor.execute('SELECT id, dia_semana, inicio, fim FROM horarios_slots WHERE barbearia_id = %s', (barbearia_id,))
        slots_rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Construir objeto no formato esperado pelo frontend
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        schedule = {}
        
        status_map = {row['dia_semana']: row['status'] for row in status_rows}
        
        slots_map = {}
        for row in slots_rows:
            day = row['dia_semana']
            if day not in slots_map: slots_map[day] = []
            
            # Formatar hora (TIME object ou string para HH:MM)
            start = str(row['inicio'])[:5]
            end = str(row['fim'])[:5]
            
            slots_map[day].append({'id': row['id'], 'start': start, 'end': end})
            
        for day in days:
            schedule[day] = {
                'status': status_map.get(day, 'closed'), # Padrão fechado se não configurado
                'slots': slots_map.get(day, [])
            }
            
        return jsonify({'success': True, 'schedule': schedule})
        
    except Exception as e:
        print(f"Erro ao buscar horários: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/barbearias/<int:barbearia_id>/horarios', methods=['POST'])
def save_horarios(barbearia_id):
    """Salva a configuração completa de horários"""
    try:
        data = request.get_json()
        schedule = data.get('schedule')
        if not schedule:
            return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
            
        conn = get_db_connection()
        if not conn: return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        
        # Estratégia simples: Limpar tudo da barbearia e inserir o novo estado
        cursor.execute('DELETE FROM horarios_slots WHERE barbearia_id = %s', (barbearia_id,))
        cursor.execute('DELETE FROM horarios_status WHERE barbearia_id = %s', (barbearia_id,))
        
        for day, info in schedule.items():
            # Salvar status
            cursor.execute('INSERT INTO horarios_status (barbearia_id, dia_semana, status) VALUES (%s, %s, %s)', 
                           (barbearia_id, day, info.get('status', 'closed')))
            # Salvar slots
            for slot in info.get('slots', []):
                cursor.execute('INSERT INTO horarios_slots (barbearia_id, dia_semana, inicio, fim) VALUES (%s, %s, %s, %s)',
                               (barbearia_id, day, slot['start'], slot['end']))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Horários salvos com sucesso'})
    except Exception as e:
        print(f"Erro ao salvar horários: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ---------- Fotos da Galeria ----------
@app.route('/api/barbearias/<int:barbearia_id>/fotos', methods=['GET'])
def list_barbearia_fotos(barbearia_id):
    """Lista fotos da galeria da barbearia"""
    try:
        conn = get_db_connection()
        if not conn: return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, foto, data_criacao FROM barbearia_fotos WHERE barbearia_id = %s ORDER BY id DESC', (barbearia_id,))
        fotos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'fotos': fotos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/barbearias/<int:barbearia_id>/fotos', methods=['POST'])
def add_barbearia_foto(barbearia_id):
    """Adiciona uma foto à galeria"""
    try:
        data = request.get_json()
        foto_base64 = data.get('foto')
        if not foto_base64: return jsonify({'success': False, 'message': 'Foto não fornecida'}), 400
        
        conn = get_db_connection()
        if not conn: return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        cursor.execute('INSERT INTO barbearia_fotos (barbearia_id, foto) VALUES (%s, %s)', (barbearia_id, foto_base64))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/barbearias/<int:barbearia_id>/fotos/<int:foto_id>', methods=['DELETE'])
def delete_barbearia_foto(barbearia_id, foto_id):
    """Remove uma foto da galeria"""
    try:
        conn = get_db_connection()
        if not conn: return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        cursor = conn.cursor()
        cursor.execute('DELETE FROM barbearia_fotos WHERE id = %s AND barbearia_id = %s', (foto_id, barbearia_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/barbearias/services', methods=['GET'])
def get_available_services():
    """Obtém lista de serviços disponíveis"""
    services = [
        "Corte masculino",
        "Barba",
        "Sobrancelha"
    ]
    
    return jsonify({
        'success': True,
        'services': services
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica se a API está funcionando"""
    return jsonify({
        'success': True,
        'message': 'API EasyCut Barbearias funcionando',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Inicializar banco de dados
    init_db()
    
    print("=" * 60)
    print("EASYCUT - API DE BARBEARIAS")
    print("=" * 60)
    print("Servidor rodando em: http://localhost:5001")
    print("Endpoints disponíveis:")
    print("  POST /api/barbearias/nearby - Buscar barbearias próximas")
    print("  POST /api/clientes - Cadastro de clientes")
    print("  POST /api/barbearias - Cadastro de barbearias")
    print("  POST /api/login    - Login de usuários")
    print("  GET  /api/clientes - Listar clientes (Verificação)")
    print("  GET  /api/barbearias/<id> - Detalhes da barbearia")
    print("  GET  /api/barbearias/<id>/servicos - Listar serviços da barbearia")
    print("  POST /api/barbearias/<id>/servicos - Cadastrar serviço")
    print("  PUT  /api/barbearias/<id>/servicos/<sid> - Atualizar serviço")
    print("  DELETE /api/barbearias/<id>/servicos/<sid> - Excluir serviço")
    print("  POST /api/agendamentos - Criar agendamento (cliente)")
    print("  GET  /api/clientes/<id>/agendamentos - Agendamentos do cliente")
    print("  GET  /api/barbearias/<id>/agendamentos - Agendamentos da barbearia")
    print("  PUT  /api/agendamentos/<id> - Atualizar status do agendamento")
    print("  GET  /api/barbearias/services - Serviços disponíveis")
    print("  GET  /api/health - Status da API")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
