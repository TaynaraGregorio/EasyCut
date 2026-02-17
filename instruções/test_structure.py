#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Script de Teste da Nova Estrutura
Testa se todos os imports estão funcionando corretamente
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Testa se todos os imports estão funcionando"""
    print("=" * 60)
    print("TESTE DE IMPORTS - NOVA ESTRUTURA EasyCut")
    print("=" * 60)
    
    try:
        # Testar imports do backend
        print("1. Testando imports do backend...")
        
        from backend.email_validator import EmailValidator
        print("   OK EmailValidator importado com sucesso")
        
        from backend.phone_validator import PhoneValidator
        print("   OK PhoneValidator importado com sucesso")
        
        from backend.cpf_cnpj_validator import CPFCNPJValidator
        print("   OK CPFCNPJValidator importado com sucesso")
        
        from backend.form_validator import FormValidator
        print("   OK FormValidator importado com sucesso")
        
        # Testar instanciação
        print("\n2. Testando instanciação das classes...")
        
        email_validator = EmailValidator()
        print("   OK EmailValidator instanciado")
        
        phone_validator = PhoneValidator()
        print("   OK PhoneValidator instanciado")
        
        cpf_cnpj_validator = CPFCNPJValidator()
        print("   OK CPFCNPJValidator instanciado")
        
        form_validator = FormValidator()
        print("   OK FormValidator instanciado")
        
        # Testar funcionalidades básicas
        print("\n3. Testando funcionalidades básicas...")
        
        # Teste de email
        email_result = email_validator.validate_email_for_form("teste@exemplo.com")
        print(f"   OK Email validation: {email_result['is_valid']}")
        
        # Teste de telefone
        phone_result = phone_validator.validate_phone_for_form("(11) 99999-9999")
        print(f"   OK Phone validation: {phone_result['is_valid']}")
        
        # Teste de CPF
        cpf_result = cpf_cnpj_validator.validate_document_for_form("11144477735")
        print(f"   OK CPF validation: {cpf_result['is_valid']}")
        
        # Teste de formulário
        form_data = {
            'nomeCompleto': 'João Silva',
            'email': 'joao@exemplo.com',
            'telefone': '(11) 99999-9999',
            'senha': 'senha123',
            'confirmarSenha': 'senha123'
        }
        form_result = form_validator.validate_client_form(form_data)
        print(f"   OK Form validation: {form_result['is_valid']}")
        
        print("\n" + "=" * 60)
        print("OK TODOS OS TESTES PASSARAM!")
        print("OK Nova estrutura funcionando perfeitamente!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ ERRO DE IMPORT: {e}")
        print("Verifique se todos os arquivos estão na pasta backend/")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        return False

def test_file_structure():
    """Testa se a estrutura de arquivos está correta"""
    print("\n4. Verificando estrutura de arquivos...")
    
    # Verificar se as pastas existem
    if os.path.exists('frontend'):
        print("   OK Pasta frontend existe")
    else:
        print("   ❌ Pasta frontend não encontrada")
        return False
    
    if os.path.exists('backend'):
        print("   OK Pasta backend existe")
    else:
        print("   ❌ Pasta backend não encontrada")
        return False
    
    # Verificar arquivos HTML no frontend
    html_files = ['CadastroCliente.html', 'CadastroBarbearia.html', 'Login.html', 'TelaInicial.html']
    for html_file in html_files:
        if os.path.exists(f'frontend/{html_file}'):
            print(f"   OK {html_file} encontrado")
        else:
            print(f"   ❌ {html_file} não encontrado")
            return False
    
    # Verificar arquivos Python no backend
    py_files = ['email_validator.py', 'phone_validator.py', 'cpf_cnpj_validator.py', 'form_validator.py', 'api_validator.py']
    for py_file in py_files:
        if os.path.exists(f'backend/{py_file}'):
            print(f"   OK {py_file} encontrado")
        else:
            print(f"   ❌ {py_file} não encontrado")
            return False
    
    # Verificar arquivos JavaScript no frontend/assets
    js_files = ['cpf_cnpj_validator_frontend.js', 'phone_validator_frontend.js', 'backend_integration.js']
    for js_file in js_files:
        if os.path.exists(f'frontend/assets/{js_file}'):
            print(f"   OK {js_file} encontrado")
        else:
            print(f"   ❌ {js_file} não encontrado")
            return False
    
    print("   OK Estrutura de arquivos está correta!")
    return True

if __name__ == "__main__":
    print("Iniciando testes da nova estrutura...")
    
    # Testar estrutura de arquivos
    if not test_file_structure():
        print("\n❌ Estrutura de arquivos incorreta!")
        sys.exit(1)
    
    # Testar imports
    if not test_imports():
        print("\n❌ Testes de import falharam!")
        sys.exit(1)
    
    print("\nSUCESSO! Nova estrutura está funcionando perfeitamente!")
    print("\nEstrutura final:")
    print("EasyCut/")
    print("|-- frontend/")
    print("|   |-- *.html")
    print("|   |-- assets/")
    print("|       |-- *.js")
    print("|-- backend/")
    print("|   |-- *.py")
    print("|   |-- requirements.txt")
    print("|-- README.md")
