/**
 * Configuração de URL para funcionar localmente e em produção
 */

window.URLConfig = {
    // URLs possíveis para teste local
    localUrls: [
        'http://localhost:3000',
        'http://localhost:8080', 
        'http://localhost:5500',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:8080',
        'http://127.0.0.1:5500'
    ],
    
    // URL de produção (substitua pela sua)
    productionUrl: 'https://seudominio.com',
    
    /**
     * Detecta a URL correta baseada no ambiente
     */
    getCorrectUrl() {
        // Se estiver em produção (https://)
        if (window.location.protocol === 'https:') {
            return window.location.origin;
        }
        
        // Se estiver em desenvolvimento local (http://)
        if (window.location.protocol === 'http:') {
            return window.location.origin;
        }
        
        // Se estiver em file:// (arquivo local), usar localhost
        if (window.location.protocol === 'file:') {
            // Tentar detectar se há um servidor local rodando
            return this.detectLocalServer();
        }
        
        // Fallback
        return 'http://localhost:3000';
    },
    
    /**
     * Detecta se há um servidor local rodando
     */
    async detectLocalServer() {
        for (const url of this.localUrls) {
            try {
                const response = await fetch(`${url}/TelaInicial.html`, { 
                    method: 'HEAD',
                    mode: 'no-cors'
                });
                console.log(`✅ Servidor local detectado: ${url}`);
                return url;
            } catch (error) {
                // Continuar tentando outras URLs
            }
        }
        
        // Se nenhum servidor local for encontrado, usar o primeiro
        console.log('⚠️ Nenhum servidor local detectado. Usando localhost:3000');
        return 'http://localhost:3000';
    },
    
    /**
     * Configura a URL no EmailService
     */
    configureEmailService() {
        if (window.emailService) {
            const correctUrl = this.getCorrectUrl();
            window.emailService.baseUrl = correctUrl;
            console.log(`🔗 URL configurada: ${correctUrl}`);
            return correctUrl;
        }
        return null;
    }
};

// Configurar automaticamente quando o script carregar
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        const url = window.URLConfig.configureEmailService();
        if (url) {
            console.log('✅ URL configurada automaticamente!');
            console.log(`🔗 Base URL: ${url}`);
        }
    }, 1000);
});

console.log('🔧 URLConfig carregado!');








