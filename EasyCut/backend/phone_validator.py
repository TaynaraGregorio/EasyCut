#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Validador de Telefone
Validação de números de telefone usando a biblioteca phonenumbers do Google
"""

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat
import re
from typing import Tuple, Dict, Any, List


class PhoneValidator:
    """
    Classe para validação de números de telefone brasileiros
    """
    
    def __init__(self):
        # Regex para telefones brasileiros
        self.phone_regex = re.compile(
            r'^(\+55\s?)?(\(?[1-9]{2}\)?)\s?([0-9]{4,5})\-?([0-9]{4})$'
        )
        
        # Regex para celular brasileiro (9 dígitos)
        self.cell_regex = re.compile(
            r'^(\+55\s?)?(\(?[1-9]{2}\)?)\s?([0-9]{5})\-?([0-9]{4})$'
        )
    
    def clean_phone_number(self, phone: str) -> str:
        """
        Remove formatação do número de telefone
        
        Args:
            phone (str): Número de telefone com formatação
            
        Returns:
            str: Número limpo apenas com dígitos
        """
        if not phone:
            return ""
        
        # Remove todos os caracteres não numéricos
        cleaned = re.sub(r'\D', '', phone)
        return cleaned
    
    def format_phone_number(self, phone: str, format_type: str = 'national') -> str:
        """
        Formata número de telefone
        
        Args:
            phone (str): Número de telefone
            format_type (str): Tipo de formatação ('national', 'international', 'e164')
            
        Returns:
            str: Número formatado
        """
        try:
            # Limpar número
            cleaned = self.clean_phone_number(phone)
            
            if not cleaned:
                return ""
            
            # Adicionar código do país se necessário
            if not cleaned.startswith('55'):
                cleaned = '55' + cleaned
            
            # Parse do número
            parsed_number = phonenumbers.parse(cleaned, "BR")
            
            # Formatar conforme solicitado
            if format_type == 'national':
                return phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL)
            elif format_type == 'international':
                return phonenumbers.format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL)
            elif format_type == 'e164':
                return phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            else:
                return phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL)
                
        except NumberParseException:
            return phone  # Retorna original se não conseguir formatar
    
    def validate_phone_format(self, phone: str) -> Tuple[bool, str]:
        """
        Valida formato básico do telefone usando regex
        
        Args:
            phone (str): Número de telefone
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem)
        """
        if not phone or not isinstance(phone, str):
            return False, "Telefone não pode estar vazio"
        
        phone = phone.strip()
        
        if not phone:
            return False, "Telefone não pode estar vazio"
        
        # Verificar se tem pelo menos 10 dígitos
        digits_only = self.clean_phone_number(phone)
        if len(digits_only) < 10:
            return False, "Telefone deve ter pelo menos 10 dígitos"
        
        if len(digits_only) > 13:  # +55 + 2 DDD + 9 dígitos máximo
            return False, "Telefone tem muitos dígitos"
        
        # Verificar formato brasileiro
        if not (self.phone_regex.match(phone) or phone.startswith('+55')):
            return False, "Formato de telefone inválido para o Brasil"
        
        return True, "Formato válido"
    
    def validate_phone_advanced(self, phone: str, country_code: str = "BR") -> Dict[str, Any]:
        """
        Validação avançada usando phonenumbers
        
        Args:
            phone (str): Número de telefone
            country_code (str): Código do país (padrão: BR)
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        result = {
            'is_valid': False,
            'phone': phone,
            'formatted_phone': None,
            'phone_type': None,
            'country_code': None,
            'national_number': None,
            'error_message': None,
            'validation_details': {}
        }
        
        try:
            # Limpar número
            cleaned = self.clean_phone_number(phone)
            
            if not cleaned:
                result['error_message'] = "Telefone não pode estar vazio"
                return result
            
            # Adicionar código do país se necessário
            if not cleaned.startswith('55') and country_code == "BR":
                cleaned = '55' + cleaned
            
            # Parse do número
            parsed_number = phonenumbers.parse(cleaned, country_code)
            
            # Verificar se é válido
            is_valid = phonenumbers.is_valid_number(parsed_number)
            
            if is_valid:
                result['is_valid'] = True
                result['formatted_phone'] = phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL)
                result['phone_type'] = self._get_phone_type(parsed_number)
                result['country_code'] = parsed_number.country_code
                result['national_number'] = parsed_number.national_number
                result['validation_details'] = {
                    'region_code': phonenumbers.region_code_for_number(parsed_number),
                    'timezone': phonenumbers.timezone.time_zones_for_number(parsed_number)
                }
            else:
                result['error_message'] = "Número de telefone inválido"
                
        except NumberParseException as e:
            result['error_message'] = f"Erro ao analisar número: {str(e)}"
            result['validation_details']['error_code'] = e.error_type
            
        except Exception as e:
            result['error_message'] = f"Erro inesperado: {str(e)}"
        
        return result
    
    def _get_phone_type(self, parsed_number) -> str:
        """
        Determina o tipo de telefone
        
        Args:
            parsed_number: Número parseado pelo phonenumbers
            
        Returns:
            str: Tipo do telefone
        """
        try:
            phone_type = phonenumbers.number_type(parsed_number)
            
            type_mapping = {
                phonenumbers.PhoneNumberType.MOBILE: "Celular",
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Celular",
                phonenumbers.PhoneNumberType.TOLL_FREE: "0800",
                phonenumbers.PhoneNumberType.PREMIUM_RATE: "Tarifa Premium",
                phonenumbers.PhoneNumberType.SHARED_COST: "Custo Compartilhado",
                phonenumbers.PhoneNumberType.VOIP: "VoIP",
                phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Pessoal",
                phonenumbers.PhoneNumberType.PAGER: "Pager",
                phonenumbers.PhoneNumberType.UAN: "UAN",
                phonenumbers.PhoneNumberType.VOICEMAIL: "Caixa Postal",
                phonenumbers.PhoneNumberType.UNKNOWN: "Desconhecido"
            }
            
            return type_mapping.get(phone_type, "Desconhecido")
            
        except Exception:
            return "Desconhecido"
    
    def validate_phone_for_form(self, phone: str) -> Dict[str, Any]:
        """
        Validação específica para formulários web
        
        Args:
            phone (str): Número de telefone
            
        Returns:
            Dict[str, Any]: Resultado formatado para uso em formulários
        """
        validation_result = self.validate_phone_advanced(phone)
        
        return {
            'is_valid': validation_result['is_valid'],
            'phone': validation_result['phone'],
            'formatted_phone': validation_result['formatted_phone'],
            'phone_type': validation_result['phone_type'],
            'message': validation_result['error_message'] or "Telefone válido",
            'can_use': validation_result['is_valid']
        }
    
    def validate_multiple_phones(self, phones: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Valida múltiplos números de telefone
        
        Args:
            phones (List[str]): Lista de telefones para validar
            
        Returns:
            Dict[str, Dict[str, Any]]: Resultados para cada telefone
        """
        results = {}
        
        for phone in phones:
            if phone:  # Ignora telefones vazios
                results[phone] = self.validate_phone_for_form(phone)
        
        return results
    
    def get_whatsapp_format(self, phone: str) -> str:
        """
        Formata número para WhatsApp
        
        Args:
            phone (str): Número de telefone
            
        Returns:
            str: Número formatado para WhatsApp
        """
        try:
            cleaned = self.clean_phone_number(phone)
            
            if not cleaned:
                return ""
            
            # Adicionar código do país se necessário
            if not cleaned.startswith('55'):
                cleaned = '55' + cleaned
            
            # Parse e formatação E164 para WhatsApp
            parsed_number = phonenumbers.parse(cleaned, "BR")
            return phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
            
        except Exception:
            return phone


def validate_phone_simple(phone: str) -> bool:
    """
    Função simples para validação rápida de telefone
    
    Args:
        phone (str): Número de telefone
        
    Returns:
        bool: True se válido, False caso contrário
    """
    validator = PhoneValidator()
    is_valid, _ = validator.validate_phone_format(phone)
    return is_valid


def validate_phone_with_details(phone: str) -> Dict[str, Any]:
    """
    Validação completa com detalhes
    
    Args:
        phone (str): Número de telefone
        
    Returns:
        Dict[str, Any]: Resultado detalhado da validação
    """
    validator = PhoneValidator()
    return validator.validate_phone_advanced(phone)


# Exemplo de uso e testes
if __name__ == "__main__":
    # Criar instância do validador
    validator = PhoneValidator()
    
    # Lista de telefones para teste
    test_phones = [
        "(11) 99999-9999",      # Celular válido
        "11999999999",          # Sem formatação
        "+55 11 99999-9999",   # Internacional
        "(21) 98765-4321",      # Rio de Janeiro
        "(85) 99999-8888",      # Fortaleza
        "1199999999",           # Muito curto
        "119999999999999",      # Muito longo
        "abc-def-ghij",         # Letras
        "",                     # Vazio
        None                    # Nulo
    ]
    
    print("=" * 70)
    print("TESTE DE VALIDAÇÃO DE TELEFONES - EasyCut")
    print("=" * 70)
    
    for phone in test_phones:
        print(f"\nTestando: '{phone}'")
        print("-" * 50)
        
        # Validação básica
        is_valid_format, format_msg = validator.validate_phone_format(phone)
        print(f"Formato básico: {'OK' if is_valid_format else 'ERRO'} - {format_msg}")
        
        # Validação avançada
        if phone:  # Só testa se não for vazio/nulo
            result = validator.validate_phone_for_form(phone)
            print(f"Validação completa: {'OK' if result['is_valid'] else 'ERRO'} - {result['message']}")
            
            if result['formatted_phone']:
                print(f"Telefone formatado: {result['formatted_phone']}")
                print(f"Tipo: {result['phone_type']}")
            
            # Formato WhatsApp
            whatsapp_format = validator.get_whatsapp_format(phone)
            if whatsapp_format:
                print(f"WhatsApp: {whatsapp_format}")
    
    print("\n" + "=" * 70)
    print("TESTE DE MÚLTIPLOS TELEFONES")
    print("=" * 70)
    
    # Teste com múltiplos telefones
    multiple_results = validator.validate_multiple_phones([
        "(11) 99999-9999",
        "(21) 98765-4321",
        "telefone-invalido",
        "(85) 99999-8888"
    ])
    
    for phone, result in multiple_results.items():
        status = "OK VÁLIDO" if result['is_valid'] else "ERRO INVÁLIDO"
        print(f"{phone}: {status} - {result['message']}")
        if result['phone_type']:
            print(f"  Tipo: {result['phone_type']}")
    
    print("\n" + "=" * 70)
    print("EXEMPLO DE USO EM FORMULÁRIO")
    print("=" * 70)
    
    # Simulação de validação em formulário
    def simulate_form_validation(phone_input):
        result = validator.validate_phone_for_form(phone_input)
        
        if result['is_valid']:
            print(f"OK Telefone '{phone_input}' é válido!")
            print(f"  Formatado: {result['formatted_phone']}")
            print(f"  Tipo: {result['phone_type']}")
            print(f"  WhatsApp: {validator.get_whatsapp_format(phone_input)}")
        else:
            print(f"ERRO Telefone '{phone_input}' é inválido: {result['message']}")
        
        return result['is_valid']
    
    # Teste com telefones do formulário
    form_phones = [
        "(11) 99999-9999",
        "(21) 98765-4321",
        "telefone-invalido",
        "(85) 99999-8888"
    ]
    
    for phone in form_phones:
        simulate_form_validation(phone)
        print()
