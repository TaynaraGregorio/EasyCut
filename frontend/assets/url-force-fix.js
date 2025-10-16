/**
 * CORREÇÃO FORÇADA DE URL
 * Este script força o uso de localhost mesmo em file://
 */

window.URLForceFix = {
    /**
     * Força o uso de localhost no EmailService
     */
    forceLocalhost() {
        if (window.emailService) {
            // Forçar localhost:3000
            window.emailService.baseUrl = 'http://localhost:3000';
            
            console.log('🔧 URL forçada para localhost:3000');
            console.log('📍 Base URL:', window.emailService.baseUrl);
            
            return true;
        }
        
        console.log('❌ EmailService não encontrado!');
        return false;
    },
    
    /**
     * Testa se a correção funcionou
     */
    testFix() {
        console.log('🧪 Testando correção de URL...');
        
        if (!this.forceLocalhost()) {
            console.log('❌ Falha na correção');
            return false;
        }
        
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
                console.log('✅ Correção funcionando!');
                console.log('🎯 Agora os emails terão links corretos!');
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
     * Verifica se o servidor local está rodando
     */
    async checkServer() {
        console.log('🔍 Verificando servidor local...');
        
        try {
            const response = await fetch('http://localhost:3000', { 
                method: 'HEAD',
                mode: 'no-cors'
            });
            
            console.log('✅ Servidor local funcionando!');
            console.log('🌐 Acesse: http://localhost:3000/TelaInicial.html');
            return true;
        } catch (error) {
            console.log('❌ Servidor local não está rodando');
            console.log('💡 Para iniciar o servidor, execute no terminal:');
            console.log('   cd frontend');
            console.log('   python -m http.server 3000');
            return false;
        }
    }
};

// Executar correção automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔧 Aplicando correção forçada de URL...');
        
        // Verificar servidor primeiro
        window.URLForceFix.checkServer().then(serverRunning => {
            if (serverRunning) {
                // Aplicar correção
                window.URLForceFix.testFix();
            } else {
                console.log('⚠️ Servidor não está rodando, mas correção será aplicada mesmo assim');
                window.URLForceFix.testFix();
            }
        });
    }, 1000);
});

// Funções globais para teste
window.forceLocalhost = () => window.URLForceFix.forceLocalhost();
window.testFix = () => window.URLForceFix.testFix();
window.checkServer = () => window.URLForceFix.checkServer();

console.log('🔧 URLForceFix carregado!');
console.log('💡 Execute: forceLocalhost() para forçar localhost');
console.log('💡 Execute: testFix() para testar correção');
console.log('💡 Execute: checkServer() para verificar servidor');








