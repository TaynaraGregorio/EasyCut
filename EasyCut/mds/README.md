# EasyCut - Validação de Email com Python

Este projeto contém validação robusta de emails usando a biblioteca `email-validator` do Python, substituindo a validação básica com regex dos formulários HTML.

## 📁 Arquivos Criados

- `email_validator.py` - Validador principal de emails
- `form_validator.py` - Validador completo de formulários
- `requirements.txt` - Dependências do projeto
- `README.md` - Este arquivo de documentação

## 🚀 Instalação

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Ou instalar manualmente:**
```bash
pip install email-validator
```

## 📖 Como Usar

### 1. Validação Simples de Email

```python
from email_validator import EmailValidator

# Criar instância do validador
validator = EmailValidator()

# Validar um email
result = validator.validate_email_for_form("usuario@exemplo.com")

if result['is_valid']:
    print(f"✓ Email válido: {result['normalized_email']}")
else:
    print(f"✗ Email inválido: {result['message']}")
```

### 2. Validação Completa de Formulários

```python
from form_validator import FormValidator

# Criar instância do validador de formulários
form_validator = FormValidator()

# Dados do formulário de cliente
client_data = {
    'nomeCompleto': 'João Silva Santos',
    'email': 'joao@exemplo.com',
    'telefone': '(11) 99999-9999',
    'senha': 'minhasenha123',
    'confirmarSenha': 'minhasenha123'
}

# Validar formulário
result = form_validator.validate_client_form(client_data)

if result['is_valid']:
    print("✓ Formulário válido!")
    print(f"Dados validados: {result['validated_data']}")
else:
    print("✗ Formulário contém erros:")
    for error in result['errors']:
        print(f"  - {error}")
```

### 3. Validação de Múltiplos Emails

```python
from email_validator import EmailValidator

validator = EmailValidator()

emails = [
    "cliente@barbearia.com",
    "contato@easycut.com.br",
    "email-invalido",
    "admin@teste.org"
]

results = validator.validate_multiple_emails(emails)

for email, result in results.items():
    status = "✓" if result['is_valid'] else "✗"
    print(f"{status} {email}: {result['message']}")
```

## 🔧 Funcionalidades

### EmailValidator

- ✅ **Validação de formato** - Verifica sintaxe básica do email
- ✅ **Validação avançada** - Usa email-validator para validação completa
- ✅ **Normalização** - Converte email para formato padrão
- ✅ **Verificação de existência** - Opcional, verifica se o email existe (mais lento)
- ✅ **Múltiplos emails** - Valida lista de emails de uma vez

### FormValidator

- ✅ **Validação de cliente** - Valida todos os campos do formulário de cliente
- ✅ **Validação de barbearia** - Valida todos os campos do formulário de barbearia
- ✅ **Mensagens de erro** - Retorna erros específicos para cada campo
- ✅ **Avisos** - Retorna avisos para campos opcionais
- ✅ **Dados normalizados** - Retorna dados limpos e validados

## 📋 Campos Validados

### Formulário de Cliente
- **Nome Completo**: Mínimo nome e sobrenome
- **Email**: Formato válido e normalizado
- **Telefone**: Mínimo 10 dígitos
- **Senha**: Mínimo 8 caracteres e confirmação

### Formulário de Barbearia
- **Nome da Barbearia**: Campo obrigatório
- **CNPJ/CPF**: 11 dígitos (CPF) ou 14 dígitos (CNPJ)
- **Responsável**: Nome completo obrigatório
- **WhatsApp**: Telefone obrigatório
- **Telefone Comercial**: Opcional, mas validado se preenchido
- **Email**: Formato válido e normalizado
- **Senha**: Mínimo 8 caracteres e confirmação

## 🌐 Integração com APIs

### Flask
```python
from flask import Flask, request, jsonify
from form_validator import FormValidator

app = Flask(__name__)
validator = FormValidator()

@app.route('/api/validate-client', methods=['POST'])
def validate_client():
    form_data = request.get_json()
    result = validator.validate_client_form(form_data)
    return jsonify(result)
```

### Django
```python
from django.http import JsonResponse
from form_validator import FormValidator

def validate_client_view(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        validator = FormValidator()
        result = validator.validate_client_form(form_data)
        return JsonResponse(result)
```

## 🧪 Testes

Execute o arquivo principal para ver os testes:

```bash
python email_validator.py
```

Ou teste o validador de formulários:

```bash
python form_validator.py
```

## 📊 Exemplos de Validação

### Emails Válidos
- `usuario@exemplo.com` ✓
- `teste@domain.co.uk` ✓
- `email+tag@example.org` ✓
- `user.name@domain.com` ✓

### Emails Inválidos
- `invalid-email` ✗ (sem @)
- `@domain.com` ✗ (sem usuário)
- `user@` ✗ (sem domínio)
- `user@domain` ✗ (sem TLD)
- `user@domain.` ✗ (TLD incompleto)

## 🔍 Vantagens sobre Regex

1. **Mais preciso**: email-validator segue RFC 5322
2. **Normalização**: Converte emails para formato padrão
3. **Verificação de existência**: Opção de verificar se email existe
4. **Mensagens claras**: Erros específicos e compreensíveis
5. **Manutenção**: Biblioteca mantida pela comunidade
6. **Performance**: Otimizada para validação rápida

## 📝 Notas Importantes

- A validação de existência (`check_deliverability=True`) é mais lenta
- Emails são normalizados automaticamente (ex: `UsEr@ExAmPlE.CoM` → `user@example.com`)
- A biblioteca `email-validator` é amplamente usada e confiável
- Compatível com Python 3.6+

## 🤝 Contribuição

Para melhorar a validação:

1. Adicione novos tipos de validação
2. Melhore as mensagens de erro
3. Adicione testes unitários
4. Otimize a performance

## 📞 Suporte

Para dúvidas sobre a validação de email:
- Consulte a documentação do [email-validator](https://github.com/JoshData/python-email-validator)
- Verifique os exemplos nos arquivos `.py`
- Execute os testes para entender o comportamento

