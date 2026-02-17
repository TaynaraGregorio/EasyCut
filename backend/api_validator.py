#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - API de Validação para Formulários
Exemplo de como integrar a validação Python com os formulários HTML
"""

from flask import Flask, request, jsonify, render_template_string
try:
    from .form_validator import FormValidator
    from .phone_validator import PhoneValidator
    from .cpf_cnpj_validator import CPFCNPJValidator
except ImportError:
    from form_validator import FormValidator
    from phone_validator import PhoneValidator
    from cpf_cnpj_validator import CPFCNPJValidator
import json

app = Flask(__name__)
validator = FormValidator()
phone_validator = PhoneValidator()
cpf_cnpj_validator = CPFCNPJValidator()

# Template HTML simples para teste
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>EasyCut - Teste de Validação</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { padding: 8px; width: 300px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 5px; }
        .success { color: green; margin-top: 5px; }
        .result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9; }
    </style>
</head>
<body>
    <h1>EasyCut - Teste de Validação Backend</h1>
    
    <h2>Cadastro de Cliente</h2>
    <form id="clientForm">
        <div class="form-group">
            <label for="nomeCompleto">Nome Completo:</label>
            <input type="text" id="nomeCompleto" name="nomeCompleto" required>
        </div>
        
        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="telefone">Telefone:</label>
            <input type="tel" id="telefone" name="telefone" required>
        </div>
        
        <div class="form-group">
            <label for="senha">Senha:</label>
            <input type="password" id="senha" name="senha" required>
        </div>
        
        <div class="form-group">
            <label for="confirmarSenha">Confirmar Senha:</label>
            <input type="password" id="confirmarSenha" name="confirmarSenha" required>
        </div>
        
        <button type="submit">Validar com Backend</button>
    </form>
    
    <div id="result" class="result" style="display: none;"></div>

    <script>
        document.getElementById('clientForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/validate-client', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                displayResult(result);
                
            } catch (error) {
                console.error('Erro:', error);
                displayResult({success: false, message: 'Erro na comunicação com o servidor'});
            }
        });
        
        function displayResult(result) {
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            
            if (result.success) {
                resultDiv.innerHTML = `
                    <h3 class="success">✓ ${result.message}</h3>
                    <p><strong>Dados validados:</strong></p>
                    <pre>${JSON.stringify(result.data, null, 2)}</pre>
                `;
            } else {
                let errorsHtml = '<h3 class="error">✗ Formulário contém erros:</h3><ul>';
                result.errors.forEach(error => {
                    errorsHtml += `<li class="error">${error}</li>`;
                });
                errorsHtml += '</ul>';
                
                if (result.warnings && result.warnings.length > 0) {
                    errorsHtml += '<h4>Avisos:</h4><ul>';
                    result.warnings.forEach(warning => {
                        errorsHtml += `<li style="color: orange;">${warning}</li>`;
                    });
                    errorsHtml += '</ul>';
                }
                
                resultDiv.innerHTML = errorsHtml;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Página principal com formulário de teste"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/validate-client', methods=['POST'])
def validate_client():
    """API para validar formulário de cliente"""
    try:
        # Obter dados do formulário
        form_data = request.get_json()
        
        # Validar com Python
        result = validator.validate_client_form(form_data)
        
        # Retornar resultado
        return jsonify({
            'success': result['is_valid'],
            'message': 'Formulário válido' if result['is_valid'] else 'Formulário contém erros',
            'errors': result['errors'],
            'warnings': result['warnings'],
            'data': result['validated_data'] if result['is_valid'] else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no servidor: {str(e)}',
            'errors': [str(e)]
        }), 500

@app.route('/api/validate-barbershop', methods=['POST'])
def validate_barbershop():
    """API para validar formulário de barbearia"""
    try:
        form_data = request.get_json()
        result = validator.validate_barbershop_form(form_data)
        
        return jsonify({
            'success': result['is_valid'],
            'message': 'Formulário válido' if result['is_valid'] else 'Formulário contém erros',
            'errors': result['errors'],
            'warnings': result['warnings'],
            'data': result['validated_data'] if result['is_valid'] else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no servidor: {str(e)}',
            'errors': [str(e)]
        }), 500

@app.route('/api/validate-email', methods=['POST'])
def validate_email_only():
    """API para validar apenas email"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        
        try:
            from .email_validator import EmailValidator
        except ImportError:
            from email_validator import EmailValidator
        email_validator = EmailValidator()
        result = email_validator.validate_email_for_form(email)
        
        return jsonify({
            'success': result['is_valid'],
            'message': result['message'],
            'email': result['email'],
            'normalized_email': result['normalized_email']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na validação: {str(e)}'
        }), 500

@app.route('/api/validate-phone', methods=['POST'])
def validate_phone_only():
    """API para validar apenas telefone"""
    try:
        data = request.get_json()
        phone = data.get('phone', '')
        
        result = phone_validator.validate_phone_for_form(phone)
        
        return jsonify({
            'success': result['is_valid'],
            'message': result['message'],
            'phone': result['phone'],
            'formatted_phone': result['formatted_phone'],
            'phone_type': result['phone_type'],
            'whatsapp_format': phone_validator.get_whatsapp_format(phone) if result['is_valid'] else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na validação: {str(e)}'
        }), 500

@app.route('/api/validate-cpf-cnpj', methods=['POST'])
def validate_cpf_cnpj_only():
    """API para validar apenas CPF/CNPJ"""
    try:
        data = request.get_json()
        document = data.get('document', '')
        
        result = cpf_cnpj_validator.validate_document_for_form(document)
        
        return jsonify({
            'success': result['is_valid'],
            'message': result['message'],
            'document': result['document'],
            'formatted_document': result['formatted_document'],
            'document_type': result['document_type']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro na validação: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("EasyCut - API de Validação")
    print("=" * 60)
    print("Servidor rodando em: http://localhost:5000")
    print("Endpoints disponíveis:")
    print("  GET  /                    - Página de teste")
    print("  POST /api/validate-client - Validar cliente")
    print("  POST /api/validate-barbershop - Validar barbearia")
    print("  POST /api/validate-email   - Validar apenas email")
    print("  POST /api/validate-phone  - Validar apenas telefone")
    print("  POST /api/validate-cpf-cnpj - Validar apenas CPF/CNPJ")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
