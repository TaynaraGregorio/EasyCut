/**
 * TESTE DE CORREÇÃO - Links de Confirmação
 * Este script testa se os links estão sendo gerados corretamente
 */

window.testLinkGeneration = function() {
    console.log('🧪 Testando geração de links...');
    
    if (typeof window.emailService === 'undefined') {
        console.error('❌ EmailService não encontrado!');
        return;
    }
    
    // Simular dados de usuário
    const testUserData = {
        email: 'teste@exemplo.com',
        nomeCompleto: 'Usuário Teste',
        senha: '123456',
        tipo: 'cliente'
    };
    
    // Testar geração de link
    const token = window.emailService.generateToken();
    const baseUrl = window.location.origin;
    const confirmationLink = `${baseUrl}/ConfirmarEmail.html?token=${token}&type=confirmation`;
    
    console.log('🔗 Base URL:', baseUrl);
    console.log('🎫 Token gerado:', token);
    console.log('🔗 Link de confirmação:', confirmationLink);
    
    // Testar se o link está correto
    const url = new URL(confirmationLink);
    const tokenParam = url.searchParams.get('token');
    const typeParam = url.searchParams.get('type');
    
    console.log('🔍 Token no link:', tokenParam);
    console.log('🔍 Tipo no link:', typeParam);
    
    if (tokenParam && typeParam === 'confirmation') {
        console.log('✅ Link gerado corretamente!');
        
        // Testar confirmação
        console.log('🧪 Testando confirmação...');
        const result = window.emailService.confirmEmail(token);
        
        if (result.success) {
            console.log('✅ Confirmação funcionando!');
        } else {
            console.log('⚠️ Confirmação falhou:', result.message);
        }
        
        return true;
    } else {
        console.error('❌ Link mal formado!');
        return false;
    }
};

window.testRealConfirmation = function() {
    console.log('🧪 Testando confirmação real...');
    
    // Verificar tokens salvos
    const emailTokens = JSON.parse(localStorage.getItem('emailTokens') || '[]');
    
    if (emailTokens.length === 0) {
        console.log('❌ Nenhum token encontrado!');
        console.log('💡 Cadastre um usuário primeiro');
        return;
    }
    
    // Pegar o último token
    const lastToken = emailTokens[emailTokens.length - 1];
    console.log('🎫 Último token:', lastToken.token);
    console.log('📧 Tipo:', lastToken.type);
    console.log('👤 Usuário:', lastToken.userData.email);
    
    // Testar confirmação
    const result = window.emailService.confirmEmail(lastToken.token);
    
    if (result.success) {
        console.log('✅ Confirmação bem-sucedida!');
        console.log('👤 Usuário confirmado:', result.user);
    } else {
        console.error('❌ Erro na confirmação:', result.message);
    }
    
    return result;
};

window.generateTestLink = function() {
    console.log('🔗 Gerando link de teste...');
    
    if (typeof window.emailService === 'undefined') {
        console.error('❌ EmailService não encontrado!');
        return;
    }
    
    const token = window.emailService.generateToken();
    const baseUrl = window.location.origin;
    const testLink = `${baseUrl}/ConfirmarEmail.html?token=${token}&type=confirmation`;
    
    console.log('🔗 Link de teste:', testLink);
    
    // Copiar para área de transferência se possível
    if (navigator.clipboard) {
        navigator.clipboard.writeText(testLink).then(() => {
            console.log('📋 Link copiado para área de transferência!');
        });
    }
    
    return testLink;
};

// Executar teste automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔧 Script de teste carregado!');
        console.log('💡 Execute: testLinkGeneration() para testar geração');
        console.log('💡 Execute: testRealConfirmation() para testar confirmação');
        console.log('💡 Execute: generateTestLink() para gerar link de teste');
    }, 1000);
});

console.log('🧪 Script de teste de links carregado!');








