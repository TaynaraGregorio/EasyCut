// Exemplo de como integrar validação backend com os formulários HTML
// Este código pode ser adicionado aos seus arquivos CadastroCliente.html e CadastroBarbearia.html

// Função para validar formulário com backend
async function validateWithBackend(formData, endpoint) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Erro na validação:', error);
        return {
            success: false,
            message: 'Erro na comunicação com o servidor',
            errors: ['Falha na conexão']
        };
    }
}

// Função para exibir resultados da validação
function displayValidationResult(result, formElement) {
    // Remove mensagens anteriores
    const existingMessages = formElement.querySelectorAll('.validation-message, .field-error-msg');
    existingMessages.forEach(msg => msg.remove());
    
    // Remove estilos de erro dos inputs
    const errorInputs = formElement.querySelectorAll('.input-error');
    errorInputs.forEach(input => {
        input.classList.remove('input-error');
        input.style.borderColor = '';
        input.style.boxShadow = '';
    });
    
    if (result.success) {
        // Sucesso - mostrar mensagem positiva
        const successMsg = document.createElement('div');
        successMsg.className = 'validation-message success-message';
        successMsg.innerHTML = `
            <div style="background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin: 16px 0; border: 1px solid #c3e6cb;">
                <strong>✓ ${result.message}</strong>
                ${result.data && result.data.email ? `<div style="margin-top: 8px; font-size: 0.9rem;">Email normalizado: ${result.data.email}</div>` : ''}
            </div>
        `;
        
        // Inserir antes do botão de submit
        const submitBtn = formElement.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.parentNode.insertBefore(successMsg, submitBtn);
        } else {
            formElement.appendChild(successMsg);
        }
        
        // Aqui você pode enviar os dados para o servidor ou redirecionar
        setTimeout(() => {
            window.location.href = 'Login.html';
        }, 1500);
        
    } else {
        // Erros - mostrar abaixo dos campos correspondentes
        let errors = result.errors || [];
        
        // Suporte para quando errors é um objeto {campo: "erro"}
        if (!Array.isArray(errors) && typeof errors === 'object') {
            const errorList = [];
            Object.keys(errors).forEach(key => {
                const input = formElement.querySelector(`#${key}, [name="${key}"]`);
                if (input) {
                    showFieldError(input, errors[key]);
                } else {
                    errorList.push(errors[key]);
                }
            });
            errors = errorList;
        }

        if (errors.length === 0 && result.message) {
            errors = [result.message];
        }
        
        const unmappedErrors = [];
        
        // Mapa de palavras-chave para IDs dos campos
        const fieldMap = {
            'nome': ['nomeCompleto', 'nomeBarbearia', 'responsavel', 'nome'],
            'email': ['email'],
            'e-mail': ['email'],
            'telefone': ['telefone', 'whatsapp', 'celular', 'tel', 'contato'],
            'whatsapp': ['whatsapp', 'telefone'],
            'senha': ['senha', 'confirmarSenha'],
            'cpf': ['cnpjCpf', 'documento'],
            'cnpj': ['cnpjCpf', 'documento'],
            'cep': ['cep'],
            'rua': ['logradouro'],
            'endereço': ['logradouro'],
            'número': ['numero'],
            'bairro': ['bairro'],
            'cidade': ['cidade'],
            'estado': ['estado', 'uf']
        };
        
        errors.forEach(error => {
            let mapped = false;
            const lowerError = error.toLowerCase();
            
            // Tenta encontrar o campo pelo nome exato dentro da mensagem de erro
            const inputs = formElement.querySelectorAll('input, select, textarea');
            for (const input of inputs) {
                const name = input.name || input.id;
                if (name && lowerError.includes(name.toLowerCase())) {
                    showFieldError(input, error);
                    mapped = true;
                    break;
                }
            }

            if (mapped) return;

            for (const [keyword, fieldIds] of Object.entries(fieldMap)) {
                if (lowerError.includes(keyword)) {
                    for (const fieldId of fieldIds) {
                        const input = formElement.querySelector(`#${fieldId}, [name="${fieldId}"]`);
                        if (input) {
                            showFieldError(input, error);
                            mapped = true;
                            break;
                        }
                    }
                }
                if (mapped) break;
            }
            
            if (!mapped) {
                unmappedErrors.push(error);
            }
        });
        
        // Se houver erros não mapeados, mostrar no topo
        if (unmappedErrors.length > 0) {
            const errorContainer = document.createElement('div');
            errorContainer.className = 'validation-message error-message';
            errorContainer.innerHTML = `
                <div style="background: #f8d7da; color: #721c24; padding: 12px; border-radius: 8px; margin-bottom: 16px; border: 1px solid #f5c6cb;">
                    <strong>✗ Atenção:</strong>
                    <ul style="margin: 8px 0 0 0; padding-left: 20px;">
                        ${unmappedErrors.map(e => `<li>${e}</li>`).join('')}
                    </ul>
                </div>
            `;
            formElement.insertBefore(errorContainer, formElement.firstChild);
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            // Rolar para o primeiro erro
            const firstError = formElement.querySelector('.input-error');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

function showFieldError(input, message) {
    input.classList.add('input-error');
    input.style.borderColor = '#dc3545';
    input.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';
    
    const msgDiv = document.createElement('div');
    msgDiv.className = 'field-error-msg';
    msgDiv.textContent = message;
    msgDiv.style.color = '#dc3545';
    msgDiv.style.fontSize = '0.85rem';
    msgDiv.style.marginTop = '2px';
    msgDiv.style.marginBottom = '5px';
    
    if (input.nextSibling) {
        input.parentNode.insertBefore(msgDiv, input.nextSibling);
    } else {
        input.parentNode.appendChild(msgDiv);
    }
}

// Inicializar listeners quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
// Modificação do evento de submit do formulário de cliente
const clientForm = document.getElementById('cadastroForm');
if (clientForm) {
    clientForm.setAttribute('novalidate', 'true'); // Desativa validação nativa do navegador
    clientForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Coletar dados do formulário
        const formData = {
            nomeCompleto: document.getElementById('nomeCompleto').value,
            email: document.getElementById('email').value,
            telefone: document.getElementById('telefone').value,
            senha: document.getElementById('senha').value,
            confirmarSenha: document.getElementById('confirmarSenha').value
        };
        
        // Mostrar loading
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Validando...';
        submitBtn.disabled = true;
        
        // Validar com backend
        const result = await validateWithBackend(formData, '/api/validate-client');
        
        // Restaurar botão
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        
        // Exibir resultado
        displayValidationResult(result, this);
    });
}

// Adicionar suporte para formulário de barbearia
const barberForm = document.getElementById('cadastroBarbeariaForm') || document.getElementById('formBarbearia');
if (barberForm) {
    barberForm.setAttribute('novalidate', 'true');
    barberForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Coletar dados (FormData é mais robusto para muitos campos)
        const formData = {};
        new FormData(this).forEach((value, key) => formData[key] = value);
        
        // Botão loading
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Validando...';
        submitBtn.disabled = true;
        
        // Enviar para API (usando endpoint de cadastro que valida e salva)
        const result = await validateWithBackend(formData, '/api/barbearias');
        
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        
        displayValidationResult(result, this);
    });
}

// Validação em tempo real do email (opcional)
const emailInput = document.getElementById('email');
if (emailInput) {
    emailInput.addEventListener('blur', async function(e) {
    const email = e.target.value.trim();
    
    if (email && email.includes('@')) {
        // Validar apenas o email
        const result = await validateWithBackend({email: email}, '/api/validate-email');
        
        if (result.success) {
            // Email válido - mostrar confirmação discreta
            e.target.style.borderColor = '#10b981';
            e.target.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
            
            // Se o email foi normalizado, atualizar o campo
            if (result.normalized_email && result.normalized_email !== email) {
                e.target.value = result.normalized_email;
            }
        } else {
            // Email inválido
            e.target.style.borderColor = '#ef4444';
            e.target.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
            
            // Mostrar mensagem de erro específica
            const existingMsg = e.target.parentNode.querySelector('.email-validation-message');
            if (existingMsg) existingMsg.remove();
            
            const errorMsg = document.createElement('div');
            errorMsg.className = 'email-validation-message';
            errorMsg.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 4px;';
            errorMsg.textContent = result.message;
            e.target.parentNode.appendChild(errorMsg);
        }
    } else {
        // Limpar estilos se campo estiver vazio
        e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        e.target.style.boxShadow = 'none';
        
        const existingMsg = e.target.parentNode.querySelector('.email-validation-message');
        if (existingMsg) existingMsg.remove();
    }
    });
}
});
