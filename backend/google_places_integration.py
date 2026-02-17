#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Google Places API Integration
Integração com Google Places para sugestões de endereços e geocoding
"""

import requests
import json
from typing import Dict, List, Any, Optional
import os
from dataclasses import dataclass

@dataclass
class PlaceResult:
    """Resultado de uma busca de local"""
    place_id: str
    formatted_address: str
    name: str
    geometry: Dict[str, Any]
    types: List[str]
    rating: Optional[float] = None
    price_level: Optional[int] = None

class GooglePlacesAPI:
    """
    Classe para integração com Google Places API
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.session = requests.Session()
    
    def get_place_autocomplete(self, query: str, location: Optional[Dict[str, float]] = None, radius: int = 50000) -> List[Dict[str, Any]]:
        """
        Busca sugestões de endereços usando Places Autocomplete
        
        Args:
            query (str): Texto de busca
            location (Dict[str, float], optional): Coordenadas {lat, lng}
            radius (int): Raio de busca em metros (padrão: 50km)
            
        Returns:
            List[Dict[str, Any]]: Lista de sugestões
        """
        url = f"{self.base_url}/place/autocomplete/json"
        
        params = {
            'input': query,
            'key': self.api_key,
            'language': 'pt-BR',
            'components': 'country:br'
        }
        
        if location:
            params['location'] = f"{location['lat']},{location['lng']}"
            params['radius'] = radius
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"Erro na API: {data['status']} - {data.get('error_message', 'Erro desconhecido')}")
                return []
            
            return data.get('predictions', [])
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return []
    
    def get_place_details(self, place_id: str) -> Optional[PlaceResult]:
        """
        Obtém detalhes completos de um local
        
        Args:
            place_id (str): ID do local
            
        Returns:
            Optional[PlaceResult]: Detalhes do local
        """
        url = f"{self.base_url}/place/details/json"
        
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'language': 'pt-BR',
            'fields': 'place_id,name,formatted_address,geometry,types,rating,price_level'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"Erro na API: {data['status']} - {data.get('error_message', 'Erro desconhecido')}")
                return None
            
            result = data['result']
            
            return PlaceResult(
                place_id=result['place_id'],
                formatted_address=result['formatted_address'],
                name=result.get('name', ''),
                geometry=result['geometry'],
                types=result.get('types', []),
                rating=result.get('rating'),
                price_level=result.get('price_level')
            )
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return None
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Converte endereço em coordenadas
        
        Args:
            address (str): Endereço para geocodificar
            
        Returns:
            Optional[Dict[str, Any]]: Coordenadas e detalhes
        """
        url = f"{self.base_url}/geocode/json"
        
        params = {
            'address': address,
            'key': self.api_key,
            'language': 'pt-BR',
            'region': 'br'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"Erro na API: {data['status']} - {data.get('error_message', 'Erro desconhecido')}")
                return None
            
            results = data.get('results', [])
            if not results:
                return None
            
            result = results[0]
            
            return {
                'formatted_address': result['formatted_address'],
                'geometry': result['geometry'],
                'place_id': result['place_id'],
                'types': result.get('types', [])
            }
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """
        Converte coordenadas em endereço
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            
        Returns:
            Optional[Dict[str, Any]]: Endereço e detalhes
        """
        url = f"{self.base_url}/geocode/json"
        
        params = {
            'latlng': f"{lat},{lng}",
            'key': self.api_key,
            'language': 'pt-BR'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"Erro na API: {data['status']} - {data.get('error_message', 'Erro desconhecido')}")
                return None
            
            results = data.get('results', [])
            if not results:
                return None
            
            result = results[0]
            
            return {
                'formatted_address': result['formatted_address'],
                'geometry': result['geometry'],
                'place_id': result['place_id'],
                'types': result.get('types', [])
            }
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return None
    
    def search_nearby_places(self, lat: float, lng: float, radius: int = 5000, place_type: str = "beauty_salon") -> List[Dict[str, Any]]:
        """
        Busca locais próximos (barbearias, salões)
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            radius (int): Raio em metros
            place_type (str): Tipo de local
            
        Returns:
            List[Dict[str, Any]]: Lista de locais próximos
        """
        url = f"{self.base_url}/place/nearbysearch/json"
        
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': place_type,
            'key': self.api_key,
            'language': 'pt-BR'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"Erro na API: {data['status']} - {data.get('error_message', 'Erro desconhecido')}")
                return []
            
            return data.get('results', [])
            
        except requests.RequestException as e:
            print(f"Erro na requisição: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return []


class PlacesService:
    """
    Serviço principal para integração com Google Places
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("API Key do Google Places é obrigatória")
        
        self.places_api = GooglePlacesAPI(self.api_key)
    
    def get_address_suggestions(self, query: str, user_location: Optional[Dict[str, float]] = None) -> List[str]:
        """
        Obtém sugestões de endereços para o frontend
        
        Args:
            query (str): Texto digitado pelo usuário
            user_location (Dict[str, float], optional): Localização do usuário
            
        Returns:
            List[str]: Lista de endereços formatados
        """
        if len(query) < 3:
            return []
        
        predictions = self.places_api.get_place_autocomplete(query, user_location)
        
        suggestions = []
        for prediction in predictions[:5]:  # Limitar a 5 sugestões
            suggestions.append(prediction['description'])
        
        return suggestions
    
    def get_coordinates_from_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Converte endereço em coordenadas
        
        Args:
            address (str): Endereço
            
        Returns:
            Optional[Dict[str, float]]: Coordenadas {lat, lng}
        """
        result = self.places_api.geocode_address(address)
        if not result:
            return None
        
        location = result['geometry']['location']
        return {
            'lat': location['lat'],
            'lng': location['lng']
        }
    
    def get_address_from_coordinates(self, lat: float, lng: float) -> Optional[str]:
        """
        Converte coordenadas em endereço
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            
        Returns:
            Optional[str]: Endereço formatado
        """
        result = self.places_api.reverse_geocode(lat, lng)
        if not result:
            return None
        
        return result['formatted_address']
    
    def find_nearby_barbearias(self, lat: float, lng: float, radius: int = 5000) -> List[Dict[str, Any]]:
        """
        Encontra barbearias próximas
        
        Args:
            lat (float): Latitude
            lng (float): Longitude
            radius (int): Raio em metros
            
        Returns:
            List[Dict[str, Any]]: Lista de barbearias
        """
        # Buscar diferentes tipos de estabelecimentos relacionados
        types_to_search = ['beauty_salon', 'hair_care', 'establishment']
        all_results = []
        
        for place_type in types_to_search:
            results = self.places_api.search_nearby_places(lat, lng, radius, place_type)
            all_results.extend(results)
        
        # Remover duplicatas por place_id
        unique_results = {}
        for result in all_results:
            place_id = result['place_id']
            if place_id not in unique_results:
                unique_results[place_id] = result
        
        return list(unique_results.values())


# Exemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("GOOGLE PLACES API - TESTE DE INTEGRAÇÃO")
    print("=" * 60)
    
    # Substitua pela sua API Key
    API_KEY = "SUA_API_KEY_AQUI"
    
    try:
        places_service = PlacesService(API_KEY)
        
        print("\n1. TESTE DE SUGESTÕES DE ENDEREÇO")
        print("-" * 40)
        
        suggestions = places_service.get_address_suggestions("Rua das Flores, Centro")
        print(f"Sugestões encontradas: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        print("\n2. TESTE DE GEOCODING")
        print("-" * 40)
        
        address = "Rua das Flores, Centro, Ipatinga - MG"
        coords = places_service.get_coordinates_from_address(address)
        if coords:
            print(f"Endereço: {address}")
            print(f"Coordenadas: {coords}")
            
            # Teste de reverse geocoding
            reverse_address = places_service.get_address_from_coordinates(coords['lat'], coords['lng'])
            print(f"Endereço reverso: {reverse_address}")
        
        print("\n3. TESTE DE BARBEARIAS PRÓXIMAS")
        print("-" * 40)
        
        # Coordenadas de exemplo (Ipatinga - MG)
        test_lat = -19.4708
        test_lng = -42.5489
        
        barbearias = places_service.find_nearby_barbearias(test_lat, test_lng, 5000)
        print(f"Barbearias encontradas: {len(barbearias)}")
        
        for i, barbearia in enumerate(barbearias[:3], 1):  # Mostrar apenas as 3 primeiras
            print(f"  {i}. {barbearia.get('name', 'Nome não disponível')}")
            print(f"     Endereço: {barbearia.get('vicinity', 'Endereço não disponível')}")
            print(f"     Avaliação: {barbearia.get('rating', 'N/A')}")
            print()
        
    except ValueError as e:
        print(f"Erro: {e}")
        print("\nPara usar esta API, você precisa:")
        print("1. Criar uma conta no Google Cloud Console")
        print("2. Ativar as APIs: Places API, Geocoding API")
        print("3. Criar uma API Key")
        print("4. Substituir 'SUA_API_KEY_AQUI' pela sua chave")
    
    print("\n" + "=" * 60)
    print("INTEGRAÇÃO COM GOOGLE PLACES CONCLUÍDA!")
    print("=" * 60)




























