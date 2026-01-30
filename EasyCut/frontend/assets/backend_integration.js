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
    const existingMessages = formElement.querySelectorAll('.validation-message');
    existingMessages.forEach(msg => msg.remove());
    
    if (result.success) {
        // Sucesso - mostrar mensagem positiva
        const successMsg = document.createElement('div');
        successMsg.className = 'validation-message success-message';
        successMsg.innerHTML = `
            <div style="background: #d4edda; color: #155724; padding: 12px; border-radius: 8px; margin: 16px 0; border: 1px solid #c3e6cb;">
                <strong>✓ ${result.message}</strong>
                <div style="margin-top: 8px; font-size: 0.9rem;">
                    Email normalizado: ${result.data.email}
                </div>
            </div>
        `;
        formElement.appendChild(successMsg);
        
        // Aqui você pode enviar os dados para o servidor ou redirecionar
        setTimeout(() => {
            alert('Cadastro realizado com sucesso!');
            window.location.href = 'Login.html';
        }, 1500);
        
    } else {
        // Erros - mostrar cada erro
        const errorContainer = document.createElement('div');
        errorContainer.className = 'validation-message error-message';
        
        let errorHtml = `
            <div style="background: #f8d7da; color: #721c24; padding: 12px; border-radius: 8px; margin: 16px 0; border: 1px solid #f5c6cb;">
                <strong>✗ Formulário contém erros:</strong>
                <ul style="margin: 8px 0 0 0; padding-left: 20px;">
        `;
        
        result.errors.forEach(error => {
            errorHtml += `<li>${error}</li>`;
        });
        
        errorHtml += '</ul>';
        
        if (result.warnings && result.warnings.length > 0) {
            errorHtml += '<div style="margin-top: 8px;"><strong>Avisos:</strong><ul style="margin: 4px 0 0 0; padding-left: 20px;">';
            result.warnings.forEach(warning => {
                errorHtml += `<li style="color: #856404;">${warning}</li>`;
            });
            errorHtml += '</ul></div>';
        }
        
        errorHtml += '</div>';
        errorContainer.innerHTML = errorHtml;
        formElement.appendChild(errorContainer);
    }
}

// Modificação do evento de submit do formulário de cliente
document.getElementById('cadastroForm').addEventListener('submit', async function(e) {
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

// Validação em tempo real do email (opcional)
document.getElementById('email').addEventListener('blur', async function(e) {
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

// Para o formulário de barbearia, use endpoint '/api/validate-barbershop'
// e colete os campos específicos da barbearia
