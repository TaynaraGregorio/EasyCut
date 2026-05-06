#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Validador de Email (Lógica Interna)
Validação de emails usando a biblioteca email-validator
"""

import email_validator as ext_email_validator
import re
from typing import Tuple, Dict, Any


class EmailValidator:
    """
    Classe para validação de emails usando email-validator
    """
    
    def __init__(self):
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
    
    def validate_email_format(self, email: str) -> Tuple[bool, str]:
        """
        Valida o formato básico do email usando regex
        
        Args:
            email (str): Email a ser validado
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem)
        """
        if not email or not isinstance(email, str):
            return False, "Email não pode estar vazio"
        
        email = email.strip()
        
        if not email:
            return False, "Email não pode estar vazio"
        
        if not self.email_regex.match(email):
            return False, "Formato de email inválido"
        
        return True, "Email válido"
    
    def validate_email_advanced(self, email: str, check_deliverability: bool = False) -> Dict[str, Any]:
        """
        Validação avançada do email usando email-validator
        
        Args:
            email (str): Email a ser validado
            check_deliverability (bool): Se deve verificar se o email existe (mais lento)
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        result = {
            'is_valid': False,
            'email': email,
            'normalized_email': None,
            'error_message': None,
            'validation_details': {}
        }
        
        try:
            # Validação básica primeiro
            format_valid, format_message = self.validate_email_format(email)
            if not format_valid:
                result['error_message'] = format_message
                return result
            
            # Validação avançada com email-validator
            validated_email = ext_email_validator.validate_email(
                email,
                check_deliverability=check_deliverability
            )
            
            result['is_valid'] = True
            result['normalized_email'] = validated_email.email
            result['validation_details'] = {
                'local': validated_email.local,
                'domain': validated_email.domain,
                'ascii_email': validated_email.ascii_email,
                'ascii_local': validated_email.ascii_local,
                'ascii_domain': validated_email.ascii_domain,
                'smtputf8': validated_email.smtputf8
            }
            
        except ext_email_validator.EmailNotValidError as e:
            result['error_message'] = "E-mail inválido"
            result['validation_details']['error_code'] = e.code
            
        except Exception as e:
            result['error_message'] = f"Erro inesperado: {str(e)}"
        
        return result
    
    def validate_email_for_form(self, email: str) -> Dict[str, Any]:
        """
        Validação específica para formulários web
        
        Args:
            email (str): Email a ser validado
            
        Returns:
            Dict[str, Any]: Resultado formatado para uso em formulários
        """
        validation_result = self.validate_email_advanced(email, check_deliverability=False)
        
        return {
            'is_valid': validation_result['is_valid'],
            'email': validation_result['email'],
            'normalized_email': validation_result['normalized_email'],
            'message': validation_result['error_message'] or "Email válido",
            'can_use': validation_result['is_valid']
        }
    
    def validate_multiple_emails(self, emails: list) -> Dict[str, Dict[str, Any]]:
        """
        Valida múltiplos emails
        
        Args:
            emails (list): Lista de emails para validar
            
        Returns:
            Dict[str, Dict[str, Any]]: Resultados para cada email
        """
        results = {}
        
        for email in emails:
            if email:  # Ignora emails vazios
                results[email] = self.validate_email_for_form(email)
        
        return results


def validate_email_simple(email: str) -> bool:
    """
    Função simples para validação rápida de email
    
    Args:
        email (str): Email a ser validado
        
    Returns:
        bool: True se válido, False caso contrário
    """
    validator = EmailValidator()
    is_valid, _ = validator.validate_email_format(email)
    return is_valid


def validate_email_with_details(email: str) -> Dict[str, Any]:
    """
    Validação completa com detalhes
    
    Args:
        email (str): Email a ser validado
        
    Returns:
        Dict[str, Any]: Resultado detalhado da validação
    """
    validator = EmailValidator()
    return validator.validate_email_advanced(email)