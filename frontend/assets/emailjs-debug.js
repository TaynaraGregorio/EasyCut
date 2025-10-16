/**
 * DEBUG EMAILJS - Ferramenta de Diagnóstico
 * Use esta função para identificar problemas no EmailJS
 */

window.debugEmailJS = function() {
    console.log('🔍 INICIANDO DIAGNÓSTICO EMAILJS...');
    
    // 1. Verificar se EmailJS está carregado
    if (typeof emailjs === 'undefined') {
        console.error('❌ EmailJS não está carregado!');
        return;
    }
    
    console.log('✅ EmailJS está carregado');
    
    // 2. Verificar configuração do serviço
    if (typeof window.emailService === 'undefined') {
        console.error('❌ EmailService não encontrado!');
        return;
    }
    
    console.log('✅ EmailService encontrado');
    
    // 3. Verificar configurações
    const config = window.emailService.emailjsConfig;
    console.log('📧 Service ID:', config.serviceId);
    console.log('📧 User ID:', config.userId);
    console.log('📧 Template Confirmação:', config.templateIdConfirmation);
    console.log('📧 Template Recuperação:', config.templateIdPasswordReset);
    
    // 4. Testar envio de email
    console.log('🧪 Testando envio de email...');
    
    const testParams = {
        to_email: 'teste@exemplo.com',
        to_name: 'Usuário Teste',
        confirmation_link: 'https://exemplo.com/teste',
        from_name: 'EasyCut'
    };
    
    emailjs.send(
        config.serviceId,
        config.templateIdConfirmation,
        testParams
    ).then(function(response) {
        console.log('✅ Email de teste enviado com sucesso!');
        console.log('📧 Response:', response);
    }).catch(function(error) {
        console.error('❌ Erro ao enviar email de teste:');
        console.error('📧 Error:', error);
        
        // Analisar o erro
        if (error.text) {
            console.log('📧 Detalhes do erro:', error.text);
        }
        
        // Sugestões baseadas no erro
        if (error.text && error.text.includes('Invalid template')) {
            console.log('💡 SUGESTÃO: Verifique se o Template ID está correto');
        }
        
        if (error.text && error.text.includes('Invalid service')) {
            console.log('💡 SUGESTÃO: Verifique se o Service ID está correto');
        }
        
        if (error.text && error.text.includes('Invalid user')) {
            console.log('💡 SUGESTÃO: Verifique se o User ID está correto');
        }
        
        if (error.text && error.text.includes('to_email')) {
            console.log('💡 SUGESTÃO: Verifique se o campo "To Email" está como {{to_email}}');
        }
    });
};

// Função para testar com dados reais
window.testRealEmail = function(email, nome) {
    console.log('🧪 Testando envio para:', email);
    
    const config = window.emailService.emailjsConfig;
    const testParams = {
        to_email: email,
        to_name: nome || 'Usuário Teste',
        confirmation_link: 'https://exemplo.com/teste',
        from_name: 'EasyCut'
    };
    
    emailjs.send(
        config.serviceId,
        config.templateIdConfirmation,
        testParams
    ).then(function(response) {
        console.log('✅ Email enviado com sucesso para:', email);
        console.log('📧 Response:', response);
    }).catch(function(error) {
        console.error('❌ Erro ao enviar para:', email);
        console.error('📧 Error:', error);
    });
};

console.log('🔧 Funções de debug carregadas!');
console.log('💡 Execute: debugEmailJS() para diagnosticar');
console.log('💡 Execute: testRealEmail("seu@email.com", "Seu Nome") para testar');








