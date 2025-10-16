/**
 * TESTE DE SERVIDOR LOCAL
 * Este script verifica se o servidor local está funcionando
 */

window.ServerTest = {
    /**
     * Testa se o servidor local está funcionando
     */
    async testServer() {
        console.log('🧪 Testando servidor local...');
        
        const ports = [3000, 8080, 5500, 8000];
        
        for (const port of ports) {
            try {
                const url = `http://localhost:${port}`;
                console.log(`🔍 Testando: ${url}`);
                
                const response = await fetch(url, { 
                    method: 'HEAD',
                    mode: 'no-cors'
                });
                
                console.log(`✅ Servidor funcionando em: ${url}`);
                return url;
            } catch (error) {
                console.log(`❌ Porta ${port} não disponível`);
            }
        }
        
        console.log('❌ Nenhum servidor local encontrado');
        return null;
    },
    
    /**
     * Inicia um servidor local se possível
     */
    startServer() {
        console.log('🚀 Tentando iniciar servidor local...');
        
        // Verificar se Python está disponível
        if (typeof window !== 'undefined') {
            console.log('💡 Para iniciar servidor local, execute no terminal:');
            console.log('   cd frontend');
            console.log('   python -m http.server 3000');
            console.log('   ou');
            console.log('   npx http-server -p 3000');
        }
    },
    
    /**
     * Testa a URL atual
     */
    testCurrentUrl() {
        console.log('🔍 Analisando URL atual...');
        console.log('📍 URL:', window.location.href);
        console.log('🌐 Protocolo:', window.location.protocol);
        console.log('📁 Caminho:', window.location.pathname);
        
        if (window.location.protocol === 'file:') {
            console.log('⚠️ Usando arquivo local (file://)');
            console.log('💡 Para melhor funcionamento, use servidor local');
            this.startServer();
        } else if (window.location.protocol === 'http:') {
            console.log('✅ Usando servidor local (http://)');
        } else if (window.location.protocol === 'https:') {
            console.log('✅ Usando servidor de produção (https://)');
        }
    }
};

// Executar teste automaticamente
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('🔧 Iniciando teste de servidor...');
        window.ServerTest.testCurrentUrl();
    }, 1000);
});

// Funções globais para teste
window.testServer = () => window.ServerTest.testServer();
window.startServer = () => window.ServerTest.startServer();
window.testCurrentUrl = () => window.ServerTest.testCurrentUrl();

console.log('🔧 ServerTest carregado!');
console.log('💡 Execute: testServer() para testar servidor');
console.log('💡 Execute: startServer() para instruções');
console.log('💡 Execute: testCurrentUrl() para analisar URL atual');








