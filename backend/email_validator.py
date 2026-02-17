#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Validador de Email
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
            result['error_message'] = str(e)
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


# Exemplo de uso e testes
if __name__ == "__main__":
    # Criar instância do validador
    validator = EmailValidator()
    
    # Lista de emails para teste
    test_emails = [
        "usuario@exemplo.com",
        "teste@domain.co.uk",
        "email+tag@example.org",
        "invalid-email",
        "@domain.com",
        "user@",
        "user@domain",
        "user@domain.",
        "user@.domain.com",
        "user@domain..com",
        "user name@domain.com",  # Espaço no local
        "user@domain name.com",  # Espaço no domínio
        "",  # Email vazio
        None  # Email nulo
    ]
    
    print("=" * 60)
    print("TESTE DE VALIDAÇÃO DE EMAILS - EasyCut")
    print("=" * 60)
    
    for email in test_emails:
        print(f"\nTestando: '{email}'")
        print("-" * 40)
        
        # Validação básica
        is_valid_format, format_msg = validator.validate_email_format(email)
        print(f"Formato básico: {'✓' if is_valid_format else '✗'} - {format_msg}")
        
        # Validação avançada
        if email:  # Só testa se não for vazio/nulo
            result = validator.validate_email_for_form(email)
            print(f"Validação completa: {'✓' if result['is_valid'] else '✗'} - {result['message']}")
            
            if result['normalized_email']:
                print(f"Email normalizado: {result['normalized_email']}")
    
    print("\n" + "=" * 60)
    print("TESTE DE MÚLTIPLOS EMAILS")
    print("=" * 60)
    
    # Teste com múltiplos emails
    multiple_results = validator.validate_multiple_emails([
        "cliente@barbearia.com",
        "contato@easycut.com.br",
        "invalid-email",
        "admin@teste.org"
    ])
    
    for email, result in multiple_results.items():
        status = "✓ VÁLIDO" if result['is_valid'] else "✗ INVÁLIDO"
        print(f"{email}: {status} - {result['message']}")
    
    print("\n" + "=" * 60)
    print("EXEMPLO DE USO EM FORMULÁRIO")
    print("=" * 60)
    
    # Simulação de validação em formulário
    def simulate_form_validation(email_input):
        result = validator.validate_email_for_form(email_input)
        
        if result['is_valid']:
            print(f"✓ Email '{email_input}' é válido!")
            if result['normalized_email'] != email_input:
                print(f"  Email normalizado: {result['normalized_email']}")
        else:
            print(f"✗ Email '{email_input}' é inválido: {result['message']}")
        
        return result['is_valid']
    
    # Teste com emails do formulário
    form_emails = [
        "cliente@exemplo.com",
        "barbearia@teste.com.br",
        "email-invalido",
        "contato@easycut.com"
    ]
    
    for email in form_emails:
        simulate_form_validation(email)
        print()
