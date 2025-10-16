/**
 * CORREÇÃO: Link de Confirmação
 * Este arquivo corrige problemas com links de confirmação
 */

// Função para corrigir URLs de confirmação
window.fixConfirmationLinks = function() {
    console.log('🔧 Corrigindo links de confirmação...');
    
    // Verificar se estamos na página de confirmação
    if (window.location.pathname.includes('ConfirmarEmail.html')) {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        const type = urlParams.get('type');
        
        console.log('🔍 Token encontrado:', token);
        console.log('🔍 Tipo encontrado:', type);
        
        if (token && type === 'confirmation') {
            console.log('✅ Link de confirmação válido!');
            
            // Aguardar EmailService carregar
            setTimeout(() => {
                if (typeof window.emailService !== 'undefined') {
                    console.log('🧪 Testando confirmação...');
                    const result = window.emailService.confirmEmail(token);
                    
                    if (result.success) {
                        console.log('✅ Confirmação bem-sucedida!');
                        console.log('👤 Usuário:', result.user);
                    } else {
                        console.error('❌ Erro na confirmação:', result.message);
                    }
                } else {
                    console.error('❌ EmailService não encontrado!');
                }
            }, 1000);
        } else {
            console.error('❌ Token ou tipo inválido!');
        }
    }
};

// Função para testar link de confirmação
window.testConfirmationLink = function(token) {
    console.log('🧪 Testando confirmação com token:', token);
    
    if (typeof window.emailService !== 'undefined') {
        const result = window.emailService.confirmEmail(token);
        
        if (result.success) {
            console.log('✅ Confirmação bem-sucedida!');
            console.log('👤 Usuário confirmado:', result.user);
            return result;
        } else {
            console.error('❌ Erro na confirmação:', result.message);
            return result;
        }
    } else {
        console.error('❌ EmailService não encontrado!');
        return { success: false, message: 'EmailService não encontrado' };
    }
};

// Função para verificar tokens salvos
window.checkSavedTokens = function() {
    console.log('🔍 Verificando tokens salvos...');
    
    const emailTokens = JSON.parse(localStorage.getItem('emailTokens') || '[]');
    const passwordTokens = JSON.parse(localStorage.getItem('passwordTokens') || '[]');
    
    console.log('📧 Tokens de email:', emailTokens.length);
    console.log('🔐 Tokens de senha:', passwordTokens.length);
    
    if (emailTokens.length > 0) {
        console.log('📧 Último token de email:', emailTokens[emailTokens.length - 1]);
    }
    
    return { emailTokens, passwordTokens };
};

// Função para limpar tokens expirados
window.cleanExpiredTokens = function() {
    console.log('🧹 Limpando tokens expirados...');
    
    const now = Date.now();
    const emailTokens = JSON.parse(localStorage.getItem('emailTokens') || '[]');
    const passwordTokens = JSON.parse(localStorage.getItem('passwordTokens') || '[]');
    
    // Limpar tokens de email expirados (24 horas)
    const validEmailTokens = emailTokens.filter(token => {
        const age = now - token.createdAt;
        return age < 24 * 60 * 60 * 1000; // 24 horas
    });
    
    // Limpar tokens de senha expirados (1 hora)
    const validPasswordTokens = passwordTokens.filter(token => {
        const age = now - token.createdAt;
        return age < 60 * 60 * 1000; // 1 hora
    });
    
    localStorage.setItem('emailTokens', JSON.stringify(validEmailTokens));
    localStorage.setItem('passwordTokens', JSON.stringify(validPasswordTokens));
    
    console.log('✅ Tokens limpos!');
    console.log('📧 Tokens de email válidos:', validEmailTokens.length);
    console.log('🔐 Tokens de senha válidos:', validPasswordTokens.length);
};

// Executar correção automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(fixConfirmationLinks, 500);
});

console.log('🔧 Script de correção de confirmação carregado!');
console.log('💡 Execute: fixConfirmationLinks() para corrigir');
console.log('💡 Execute: testConfirmationLink("token") para testar');
console.log('💡 Execute: checkSavedTokens() para verificar tokens');
console.log('💡 Execute: cleanExpiredTokens() para limpar tokens expirados');








