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
from dataclasses import dataclass, asdict
from datetime import datetime, time
import os

# Importar integração com Google Places
try:
    from .google_places_integration import PlacesService
except ImportError:
    from google_places_integration import PlacesService

app = Flask(__name__)
CORS(app)  # Permitir CORS para frontend

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
        
        # Dados mock para desenvolvimento
        self.mock_barbearias = self._load_mock_data()
    
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
    
    def find_nearby_barbearias(self, lat: float, lng: float, radius: float = 5.0, filters: Optional[FilterOptions] = None) -> List[Dict[str, Any]]:
        """
        Encontra barbearias próximas com filtros
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            radius (float): Raio em km
            filters (FilterOptions, optional): Filtros aplicados
            
        Returns:
            List[Dict[str, Any]]: Lista de barbearias
        """
        # Se Google Places estiver disponível, usar dados reais
        if self.places_service:
            return self._find_real_barbearias(lat, lng, radius, filters)
        
        # Caso contrário, usar dados mock
        return self._find_mock_barbearias(lat, lng, radius, filters)
    
    def _find_mock_barbearias(self, lat: float, lng: float, radius: float, filters: Optional[FilterOptions]) -> List[Dict[str, Any]]:
        """Busca barbearias usando dados mock"""
        import math
        
        # Calcular distâncias e filtrar por raio
        barbearias_with_distance = []
        for barbearia in self.mock_barbearias:
            distance = self._calculate_distance(lat, lng, barbearia.latitude, barbearia.longitude)
            if distance <= radius:
                barbearia.distance = distance
                barbearias_with_distance.append(barbearia)
        
        # Aplicar filtros
        if filters:
            barbearias_with_distance = self._apply_filters(barbearias_with_distance, filters)
        
        # Ordenar por distância
        barbearias_with_distance.sort(key=lambda x: x.distance)
        
        # Converter para dict
        return [asdict(barbearia) for barbearia in barbearias_with_distance]
    
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
            # Fallback para dados mock
            return self._find_mock_barbearias(lat, lng, radius, filters)
    
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
        """Obtém detalhes de uma barbearia específica"""
        for barbearia in self.mock_barbearias:
            if barbearia.id == barbearia_id:
                return asdict(barbearia)
        return None

# Inicializar serviço
barbearias_service = BarbeariasService()

# Rotas da API
@app.route('/api/barbearias/nearby', methods=['POST'])
def get_nearby_barbearias():
    """Busca barbearias próximas"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'message': 'Latitude e longitude são obrigatórios',
                'barbearias': []
            }), 400
        
        lat = float(data['latitude'])
        lng = float(data['longitude'])
        radius = float(data.get('radius', 5.0))  # Padrão: 5km
        
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
        barbearias = barbearias_service.find_nearby_barbearias(lat, lng, radius, filters)
        
        return jsonify({
            'success': True,
            'message': f'Encontradas {len(barbearias)} barbearias',
            'barbearias': barbearias,
            'total': len(barbearias)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar barbearias: {str(e)}',
            'barbearias': []
        }), 500

@app.route('/api/barbearias/<barbearia_id>', methods=['GET'])
def get_barbearia_details(barbearia_id):
    """Obtém detalhes de uma barbearia específica"""
    try:
        barbearia = barbearias_service.get_barbearia_by_id(barbearia_id)
        
        if not barbearia:
            return jsonify({
                'success': False,
                'message': 'Barbearia não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Barbearia encontrada',
            'barbearia': barbearia
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar barbearia: {str(e)}'
        }), 500

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
    print("=" * 60)
    print("EASYCUT - API DE BARBEARIAS")
    print("=" * 60)
    print("Servidor rodando em: http://localhost:5001")
    print("Endpoints disponíveis:")
    print("  POST /api/barbearias/nearby - Buscar barbearias próximas")
    print("  GET  /api/barbearias/<id> - Detalhes da barbearia")
    print("  GET  /api/barbearias/services - Serviços disponíveis")
    print("  GET  /api/health - Status da API")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
