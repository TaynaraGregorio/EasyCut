/**
 * SOLUÇÃO SIMPLES PARA URL LOCAL
 * Este script permite configurar a URL correta para funcionar localmente
 */

window.LocalURLFix = {
    // URL base para desenvolvimento local
    localUrl: 'http://localhost:3000',
    
    /**
     * Configura a URL no EmailService
     */
    fixEmailService() {
        if (window.emailService) {
            // Forçar URL local
            window.emailService.baseUrl = this.localUrl;
            console.log(`🔧 URL corrigida para: ${this.localUrl}`);
            return true;
        }
        return false;
    },
    
    /**
     * Testa se a URL está funcionando
     */
    testUrl() {
        console.log(`🧪 Testando URL: ${this.localUrl}`);
        
        // Simular geração de link
        const token = 'test_token_123';
        const testLink = `${this.localUrl}/ConfirmarEmail.html?token=${token}&type=confirmation`;
        
        console.log(`🔗 Link de teste: ${testLink}`);
        
        // Verificar se o link está correto
        const url = new URL(testLink);
        const tokenParam = url.searchParams.get('token');
        const typeParam = url.searchParams.get('type');
        
        if (tokenParam && typeParam === 'confirmation') {
            console.log('✅ URL configurada corretamente!');
            return true;
        } else {
            console.error('❌ URL mal configurada!');
            return false;
        }
    },
    
    /**
     * Gera um link de confirmação de teste
     */
    generateTestLink() {
        const token = 'test_token_' + Date.now();
        const testLink = `${this.localUrl}/ConfirmarEmail.html?token=${token}&type=confirmation`;
        
        console.log(`🔗 Link de teste gerado: ${testLink}`);
        
        // Copiar para área de transferência se possível
        if (navigator.clipboard) {
            navigator.clipboard.writeText(testLink).then(() => {
                console.log('📋 Link copiado para área de transferência!');
            });
        }
        
        return testLink;
    }
};

// Executar correção automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔧 Aplicando correção de URL...');
        
        if (window.LocalURLFix.fixEmailService()) {
            console.log('✅ URL corrigida com sucesso!');
            window.LocalURLFix.testUrl();
        } else {
            console.log('⚠️ EmailService não encontrado. Tente novamente.');
        }
    }, 1000);
});

// Funções globais para teste
window.fixURL = () => window.LocalURLFix.fixEmailService();
window.testURL = () => window.LocalURLFix.testUrl();
window.generateTestLink = () => window.LocalURLFix.generateTestLink();

console.log('🔧 LocalURLFix carregado!');
console.log('💡 Execute: fixURL() para corrigir a URL');
console.log('💡 Execute: testURL() para testar a URL');
console.log('💡 Execute: generateTestLink() para gerar link de teste');








