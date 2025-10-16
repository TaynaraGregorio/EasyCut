/**
 * SOLUÇÃO DEFINITIVA PARA URL
 * Este script detecta automaticamente a URL correta
 */

window.URLDetector = {
    /**
     * Detecta a URL correta automaticamente
     */
    detectCorrectUrl() {
        console.log('🔍 Detectando URL correta...');
        console.log('📍 URL atual:', window.location.href);
        console.log('🌐 Protocolo:', window.location.protocol);
        console.log('📁 Caminho:', window.location.pathname);
        
        // Se estiver em file://
        if (window.location.protocol === 'file:') {
            const currentPath = window.location.pathname;
            const pathParts = currentPath.split('/');
            
            // Encontrar a pasta frontend
            const frontendIndex = pathParts.findIndex(part => part === 'frontend');
            
            if (frontendIndex !== -1) {
                // Construir URL base
                const basePath = pathParts.slice(0, frontendIndex + 1).join('/');
                const correctUrl = `file://${basePath}`;
                
                console.log('✅ URL detectada:', correctUrl);
                return correctUrl;
            }
        }
        
        // Se estiver em servidor
        if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            console.log('✅ URL do servidor:', window.location.origin);
            return window.location.origin;
        }
        
        // Fallback
        console.log('⚠️ Usando fallback');
        return window.location.href.replace(/\/[^\/]*$/, '');
    },
    
    /**
     * Configura a URL no EmailService
     */
    configureEmailService() {
        if (window.emailService) {
            const correctUrl = this.detectCorrectUrl();
            window.emailService.baseUrl = correctUrl;
            
            console.log('🔧 URL configurada no EmailService:', correctUrl);
            return correctUrl;
        }
        
        console.log('❌ EmailService não encontrado!');
        return null;
    },
    
    /**
     * Testa a configuração
     */
    testConfiguration() {
        console.log('🧪 Testando configuração...');
        
        const url = this.configureEmailService();
        if (!url) {
            console.log('❌ Falha na configuração');
            return false;
        }
        
        // Testar geração de link
        const token = 'test_token_123';
        const testLink = `${url}/ConfirmarEmail.html?token=${token}&type=confirmation`;
        
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
    }
};

// Executar detecção automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔧 Iniciando detecção automática de URL...');
        window.URLDetector.testConfiguration();
    }, 1000);
});

// Funções globais para teste
window.detectURL = () => window.URLDetector.detectCorrectUrl();
window.configureURL = () => window.URLDetector.configureEmailService();
window.testURL = () => window.URLDetector.testConfiguration();

console.log('🔧 URLDetector carregado!');
console.log('💡 Execute: detectURL() para detectar URL');
console.log('💡 Execute: configureURL() para configurar EmailService');
console.log('💡 Execute: testURL() para testar configuração');








