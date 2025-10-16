/**
 * SOLUÇÃO SEM SERVIDOR LOCAL
 * Este script faz o sistema funcionar mesmo sem servidor local
 */

window.NoServerFix = {
    /**
     * Configura URL que funciona sem servidor local
     */
    configureForNoServer() {
        if (window.emailService) {
            // Usar uma URL que funciona mesmo sem servidor
            window.emailService.baseUrl = 'https://seudominio.com'; // Substitua pelo seu domínio
            
            console.log('🔧 Configurado para funcionar sem servidor local');
            console.log('📍 Base URL:', window.emailService.baseUrl);
            console.log('💡 Em produção, substitua pelo seu domínio real');
            
            return true;
        }
        
        console.log('❌ EmailService não encontrado!');
        return false;
    },
    
    /**
     * Configura para desenvolvimento local (com fallback)
     */
    configureForDevelopment() {
        if (window.emailService) {
            // Tentar localhost primeiro, depois fallback para domínio
            const isLocalhost = window.location.href.includes('localhost') || 
                               window.location.href.includes('127.0.0.1');
            
            if (isLocalhost) {
                window.emailService.baseUrl = window.location.origin;
                console.log('✅ Usando servidor local:', window.emailService.baseUrl);
            } else {
                // Fallback para domínio de produção
                window.emailService.baseUrl = 'https://seudominio.com';
                console.log('⚠️ Usando fallback para produção:', window.emailService.baseUrl);
            }
            
            return true;
        }
        
        return false;
    },
    
    /**
     * Testa a configuração atual
     */
    testConfiguration() {
        console.log('🧪 Testando configuração...');
        
        if (!window.emailService) {
            console.log('❌ EmailService não encontrado');
            return false;
        }
        
        console.log('📍 URL atual:', window.location.href);
        console.log('🔗 Base URL configurada:', window.emailService.baseUrl);
        
        // Testar geração de link
        const token = 'test_token_' + Date.now();
        const testLink = `${window.emailService.baseUrl}/ConfirmarEmail.html?token=${token}&type=confirmation`;
        
        console.log('🔗 Link de teste:', testLink);
        
        // Verificar se o link está correto
        try {
            const urlObj = new URL(testLink);
            const tokenParam = urlObj.searchParams.get('token');
            const typeParam = urlObj.searchParams.get('type');
            
            if (tokenParam && typeParam === 'confirmation') {
                console.log('✅ Configuração funcionando!');
                return true;
            } else {
                console.log('❌ Link mal formado');
                return false;
            }
        } catch (error) {
            console.log('❌ Erro ao testar URL:', error);
            return false;
        }
    },
    
    /**
     * Instruções para configurar domínio de produção
     */
    showProductionInstructions() {
        console.log('📋 INSTRUÇÕES PARA PRODUÇÃO:');
        console.log('1. Substitua "https://seudominio.com" pelo seu domínio real');
        console.log('2. Faça upload dos arquivos para seu servidor');
        console.log('3. Configure EmailJS com seu domínio');
        console.log('4. Teste o sistema em produção');
        console.log('');
        console.log('💡 Exemplo:');
        console.log('   window.emailService.baseUrl = "https://meusite.com";');
    }
};

// Executar configuração automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔧 Configurando sistema para funcionar sem servidor local...');
        
        // Tentar configuração de desenvolvimento primeiro
        if (window.NoServerFix.configureForDevelopment()) {
            window.NoServerFix.testConfiguration();
        } else {
            // Fallback para configuração sem servidor
            window.NoServerFix.configureForNoServer();
            window.NoServerFix.showProductionInstructions();
        }
    }, 1000);
});

// Funções globais para teste
window.configureNoServer = () => window.NoServerFix.configureForNoServer();
window.configureDevelopment = () => window.NoServerFix.configureForDevelopment();
window.testConfig = () => window.NoServerFix.testConfiguration();
window.showInstructions = () => window.NoServerFix.showProductionInstructions();

console.log('🔧 NoServerFix carregado!');
console.log('💡 Execute: configureNoServer() para configurar sem servidor');
console.log('💡 Execute: configureDevelopment() para configuração de desenvolvimento');
console.log('💡 Execute: testConfig() para testar configuração');
console.log('💡 Execute: showInstructions() para ver instruções de produção');








