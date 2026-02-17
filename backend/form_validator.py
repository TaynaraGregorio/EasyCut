#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Exemplo de Integração com Formulários HTML
Como usar o validador de email com os formulários de cadastro
"""

try:
    from .email_validator import EmailValidator
    from .phone_validator import PhoneValidator
    from .cpf_cnpj_validator import CPFCNPJValidator
except ImportError:
    from email_validator import EmailValidator
    from phone_validator import PhoneValidator
    from cpf_cnpj_validator import CPFCNPJValidator
import json
from typing import Dict, Any


class FormValidator:
    """
    Classe para validação de formulários EasyCut
    """
    
    def __init__(self):
        self.email_validator = EmailValidator()
        self.phone_validator = PhoneValidator()
        self.cpf_cnpj_validator = CPFCNPJValidator()
    
    def validate_client_form(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Valida formulário de cadastro de cliente
        
        Args:
            form_data (Dict[str, str]): Dados do formulário
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        errors = []
        warnings = []
        validated_data = {}
        
        # Validar nome completo
        nome_completo = form_data.get('nomeCompleto', '').strip()
        if not nome_completo:
            errors.append("Nome completo é obrigatório")
        elif len(nome_completo.split()) < 2:
            errors.append("Nome completo deve conter pelo menos nome e sobrenome")
        else:
            validated_data['nomeCompleto'] = nome_completo
        
        # Validar email
        email = form_data.get('email', '').strip()
        if not email:
            errors.append("Email é obrigatório")
        else:
            email_result = self.email_validator.validate_email_for_form(email)
            if not email_result['is_valid']:
                errors.append(f"Email inválido: {email_result['message']}")
            else:
                validated_data['email'] = email_result['normalized_email']
        
        # Validar telefone
        telefone = form_data.get('telefone', '').strip()
        if not telefone:
            errors.append("Telefone é obrigatório")
        else:
            phone_result = self.phone_validator.validate_phone_for_form(telefone)
            if not phone_result['is_valid']:
                errors.append(f"Telefone inválido: {phone_result['message']}")
            else:
                validated_data['telefone'] = phone_result['formatted_phone']
                validated_data['telefone_whatsapp'] = self.phone_validator.get_whatsapp_format(telefone)
                validated_data['telefone_tipo'] = phone_result['phone_type']
        
        # Validar senhas
        senha = form_data.get('senha', '')
        confirmar_senha = form_data.get('confirmarSenha', '')
        
        if not senha:
            errors.append("Senha é obrigatória")
        elif len(senha) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        elif senha != confirmar_senha:
            errors.append("Senhas não coincidem")
        else:
            validated_data['senha'] = senha
        
        # Validar aceite dos termos de uso
        aceitar_termos = form_data.get('aceitarTermos', False)
        if not aceitar_termos:
            errors.append("Você deve aceitar os Termos de Uso para continuar")
        else:
            validated_data['aceitarTermos'] = True
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_data': validated_data
        }
    
    def validate_barbershop_form(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Valida formulário de cadastro de barbearia
        
        Args:
            form_data (Dict[str, str]): Dados do formulário
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        errors = []
        warnings = []
        validated_data = {}
        
        # Validar nome da barbearia
        nome_barbearia = form_data.get('nomeBarbearia', '').strip()
        if not nome_barbearia:
            errors.append("Nome da barbearia é obrigatório")
        else:
            validated_data['nomeBarbearia'] = nome_barbearia
        
        # Validar CNPJ/CPF
        cnpj_cpf = form_data.get('cnpjCpf', '').strip()
        if not cnpj_cpf:
            errors.append("CNPJ/CPF é obrigatório")
        else:
            cnpj_cpf_result = self.cpf_cnpj_validator.validate_document_for_form(cnpj_cpf)
            if not cnpj_cpf_result['is_valid']:
                errors.append(f"CNPJ/CPF inválido: {cnpj_cpf_result['message']}")
            else:
                validated_data['cnpjCpf'] = cnpj_cpf_result['formatted_document']
                validated_data['cnpjCpf_tipo'] = cnpj_cpf_result['document_type']
        
        # Validar responsável
        responsavel = form_data.get('responsavel', '').strip()
        if not responsavel:
            errors.append("Nome do responsável é obrigatório")
        elif len(responsavel.split()) < 2:
            errors.append("Nome do responsável deve conter nome e sobrenome")
        else:
            validated_data['responsavel'] = responsavel
        
        # Validar WhatsApp (obrigatório)
        whatsapp = form_data.get('whatsapp', '').strip()
        if not whatsapp:
            errors.append("WhatsApp é obrigatório")
        else:
            whatsapp_result = self.phone_validator.validate_phone_for_form(whatsapp)
            if not whatsapp_result['is_valid']:
                errors.append(f"WhatsApp inválido: {whatsapp_result['message']}")
            else:
                validated_data['whatsapp'] = whatsapp_result['formatted_phone']
                validated_data['whatsapp_e164'] = self.phone_validator.get_whatsapp_format(whatsapp)
                validated_data['whatsapp_tipo'] = whatsapp_result['phone_type']
        
        # Validar email
        email = form_data.get('email', '').strip()
        if not email:
            errors.append("Email é obrigatório")
        else:
            email_result = self.email_validator.validate_email_for_form(email)
            if not email_result['is_valid']:
                errors.append(f"Email inválido: {email_result['message']}")
            else:
                validated_data['email'] = email_result['normalized_email']
        
        # Validar senhas
        senha = form_data.get('senha', '')
        confirmar_senha = form_data.get('confirmarSenha', '')
        
        if not senha:
            errors.append("Senha é obrigatória")
        elif len(senha) < 8:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        elif senha != confirmar_senha:
            errors.append("Senhas não coincidem")
        else:
            validated_data['senha'] = senha
        
        # Validar aceite dos termos de uso
        aceitar_termos = form_data.get('aceitarTermos', False)
        if not aceitar_termos:
            errors.append("Você deve aceitar os Termos de Uso para continuar")
        else:
            validated_data['aceitarTermos'] = True
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_data': validated_data
        }


def create_api_response(validation_result: Dict[str, Any]) -> str:
    """
    Cria resposta JSON para API
    
    Args:
        validation_result (Dict[str, Any]): Resultado da validação
        
    Returns:
        str: Resposta JSON formatada
    """
    response = {
        'success': validation_result['is_valid'],
        'message': 'Formulário válido' if validation_result['is_valid'] else 'Formulário contém erros',
        'errors': validation_result['errors'],
        'warnings': validation_result['warnings']
    }
    
    if validation_result['is_valid']:
        response['data'] = validation_result['validated_data']
    
    return json.dumps(response, ensure_ascii=False, indent=2)


# Exemplo de uso
if __name__ == "__main__":
    validator = FormValidator()
    
    print("=" * 60)
    print("EXEMPLO DE VALIDAÇÃO DE FORMULÁRIOS - EasyCut")
    print("=" * 60)
    
    # Exemplo 1: Cadastro de Cliente
    print("\n1. CADASTRO DE CLIENTE")
    print("-" * 30)
    
    client_data = {
        'nomeCompleto': 'João Silva Santos',
        'email': 'joao.silva@exemplo.com',
        'telefone': '(11) 99999-9999',
        'senha': 'minhasenha123',
        'confirmarSenha': 'minhasenha123'
    }
    
    client_result = validator.validate_client_form(client_data)
    print(f"Válido: {'✓' if client_result['is_valid'] else '✗'}")
    
    if client_result['errors']:
        print("Erros:")
        for error in client_result['errors']:
            print(f"  - {error}")
    
    if client_result['warnings']:
        print("Avisos:")
        for warning in client_result['warnings']:
            print(f"  - {warning}")
    
    # Exemplo 2: Cadastro de Barbearia
    print("\n2. CADASTRO DE BARBEARIA")
    print("-" * 30)
    
    barbershop_data = {
        'nomeBarbearia': 'Barbearia do João',
        'cnpjCpf': '12.345.678/0001-90',
        'responsavel': 'João Silva Santos',
        'telefone': '(11) 1234-5678',
        'whatsapp': '(11) 99999-9999',
        'email': 'contato@barbearia.com',
        'senha': 'senhabarbearia123',
        'confirmarSenha': 'senhabarbearia123'
    }
    
    barbershop_result = validator.validate_barbershop_form(barbershop_data)
    print(f"Válido: {'✓' if barbershop_result['is_valid'] else '✗'}")
    
    if barbershop_result['errors']:
        print("Erros:")
        for error in barbershop_result['errors']:
            print(f"  - {error}")
    
    if barbershop_result['warnings']:
        print("Avisos:")
        for warning in barbershop_result['warnings']:
            print(f"  - {warning}")
    
    # Exemplo 3: Resposta JSON para API
    print("\n3. RESPOSTA JSON PARA API")
    print("-" * 30)
    
    api_response = create_api_response(client_result)
    print(api_response)
    
    print("\n" + "=" * 60)
    print("COMO USAR EM FLASK/DJANGO")
    print("=" * 60)
    
    print("""
# Exemplo para Flask:
from flask import Flask, request, jsonify
from form_validator import FormValidator

app = Flask(__name__)
validator = FormValidator()

@app.route('/api/validate-client', methods=['POST'])
def validate_client():
    form_data = request.get_json()
    result = validator.validate_client_form(form_data)
    return jsonify(result)

@app.route('/api/validate-barbershop', methods=['POST'])
def validate_barbershop():
    form_data = request.get_json()
    result = validator.validate_barbershop_form(form_data)
    return jsonify(result)

# Exemplo para Django:
from django.http import JsonResponse
from form_validator import FormValidator

def validate_client_view(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        validator = FormValidator()
        result = validator.validate_client_form(form_data)
        return JsonResponse(result)
    """)
