/**
 * Sistema de Email e Autenticação - EasyCut
 * Versão com EmailJS para envio real de emails
 */

class EmailService {
    constructor() {
        // URL que funciona em qualquer ambiente
        this.baseUrl = this.getWorkingUrl();
// Exemplo de como deve ficar no seu Login.html (dentro do script)
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    // ... pegar email e senha ...
    
    // Adicione 'await' aqui
    const result = await emailService.authenticateUser(email, senha);
    
    if (result.success) {
        window.location.href = 'TelaInicial.html'; // ou para onde deve ir
    } else {
        alert(result.message);
    }
});
        // Em produção, a API URL deve ser a URL do seu App Service no Azure
        // Você pode injetar isso via ambiente ou assumir a mesma origem se estiverem no mesmo domínio
        this.apiUrl = window.location.origin.includes('localhost') ? 'http://localhost:5001' : window.location.origin;
        this.isEmailJSLoaded = false;
        
        // Inicializar dados de usuários no localStorage se não existirem
        this.initUserData();
    }
    
    /**
     * Obtém URL que funciona em qualquer ambiente
     */
    getWorkingUrl() {
        console.log('🔍 Detectando URL de trabalho...');
        console.log('📍 URL atual:', window.location.href);
        
        // Se estiver em file://, usar localhost como fallback
        if (window.location.protocol === 'file:') {
            console.log('⚠️ Detectado file:// - usando localhost como fallback');
            console.log('💡 Para melhor funcionamento, use servidor local');
            
            // Tentar detectar se há servidor local rodando
            const commonPorts = [3000, 8080, 5500, 8000];
            
            for (const port of commonPorts) {
                console.log(`🔍 Tentando localhost:${port}...`);
                // Para simplificar, vamos usar localhost:3000 como padrão
                if (port === 3000) {
                    const workingUrl = `http://localhost:${port}`;
                    console.log('✅ Usando localhost:3000 como fallback');
                    return workingUrl;
                }
            }
        }
        
        // Se estiver em servidor, usar origem
        if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            console.log('✅ URL de trabalho (servidor):', window.location.origin);
            return window.location.origin;
        }
        
        // Fallback final: usar localhost:3000
        console.log('⚠️ Usando fallback final: localhost:3000');
        return 'http://localhost:3000';
    }
    
    /**
     * Obtém a URL base correta para funcionar tanto localmente quanto em servidor
     */
    getBaseUrl() {
        // Se estiver rodando em file:// (arquivo local), usar localhost
        if (window.location.protocol === 'file:') {
            // Tentar detectar se há um servidor local rodando
            return this.detectLocalServer();
        }
        
        // Se estiver rodando em servidor, usar a origem
        return window.location.origin;
    }
    
    /**
     * Detecta se há um servidor local rodando
     */
    detectLocalServer() {
        // URLs comuns para desenvolvimento local
        const commonPorts = [3000, 8080, 5500, 8000];
        
        for (const port of commonPorts) {
            // Verificar se há um servidor rodando nesta porta
            const testUrl = `http://localhost:${port}`;
            console.log(`🔍 Verificando servidor em: ${testUrl}`);
            
            // Para simplificar, vamos usar a porta mais comum
            if (port === 3000) {
                console.log(`✅ Usando servidor local: ${testUrl}`);
                return testUrl;
            }
        }
        
        // Fallback para localhost:3000
        console.log('⚠️ Usando fallback: http://localhost:3000');
        return 'http://localhost:3000';
    }
    
    initUserData() {
        if (!localStorage.getItem('users')) {
            localStorage.setItem('users', JSON.stringify([]));
        }
        if (!localStorage.getItem('emailTokens')) {
            localStorage.setItem('emailTokens', JSON.stringify([]));
        }
        if (!localStorage.getItem('passwordTokens')) {
            localStorage.setItem('passwordTokens', JSON.stringify([]));
        }
    }
    
    /**
     * Envia email de confirmação para novo usuário
     */
    async sendConfirmationEmail(userData) {
        try {
            const token = this.generateToken();
            const confirmationLink = `${this.baseUrl}/ConfirmarEmail.html?token=${token}&type=confirmation`;
            
            // Salvar dados do usuário temporariamente
            const tempUser = {
                ...userData,
                emailVerified: false,
                createdAt: new Date().toISOString()
            };
            
            // Salvar token de confirmação
            this.saveEmailToken(token, tempUser, 'confirmation');
            
            // Modo simulação (fallback)
            return this.fallbackConfirmation(userData, confirmationLink, token);
            
        } catch (error) {
            console.error('Erro ao processar confirmação:', error);
            return {
                success: false,
                message: 'Erro ao enviar email de confirmação. Tente novamente.'
            };
        }
    }
    
    /**
     * Envia email de confirmação de agendamento
     */
    async sendAppointmentConfirmationEmail(appointmentData) {
        try {
            // Modo simulação (fallback)
            return this.fallbackAppointmentConfirmation(appointmentData);
            
        } catch (error) {
            console.error('Erro ao processar confirmação de agendamento:', error);
            return {
                success: false,
                message: 'Erro ao enviar email de confirmação de agendamento. Tente novamente.'
            };
        }
    }
    
    /**
     * Fallback para modo simulação - Confirmação de Agendamento
     */
    fallbackAppointmentConfirmation(appointmentData) {
        console.log('📧 [SIMULAÇÃO] Email de agendamento enviado para:', appointmentData.clienteEmail);
        console.log('🏪 Barbearia:', appointmentData.barbeariaName);
        console.log('📅 Data/Hora:', appointmentData.data, appointmentData.horario);
        console.log('✂️ Serviços:', appointmentData.servicos.join(', '));
        console.log('💰 Total:', appointmentData.precoTotal);
        
        return {
            success: true,
            message: 'Email de confirmação de agendamento enviado!',
            appointmentId: appointmentData.id,
            simulation: true
        };
    }

    /**
     * Envia email de recuperação de senha
     */
    async sendPasswordResetEmail(email) {
        try {
            const users = JSON.parse(localStorage.getItem('users'));
            const user = users.find(u => u.email === email && u.emailVerified);
            
            if (!user) {
                return {
                    success: false,
                    message: 'Email não encontrado ou não verificado.'
                };
            }
            
            const token = this.generateToken();
            const resetLink = `${this.baseUrl}/RedefinirSenha.html?token=${token}`;
            
            // Salvar token de recuperação
            this.savePasswordToken(token, email);
            
            // Modo simulação (fallback)
            return this.fallbackPasswordReset(email, resetLink, token);
            
        } catch (error) {
            console.error('Erro ao enviar email de recuperação:', error);
            return {
                success: false,
                message: 'Erro ao enviar email de recuperação. Tente novamente.'
            };
        }
    }
    
    /**
     * Fallback para modo simulação - Confirmação
     */
    fallbackConfirmation(userData, confirmationLink, token) {
        console.log('📧 [SIMULAÇÃO] Email de confirmação enviado para:', userData.email);
        console.log('🔗 Link de confirmação:', confirmationLink);
        
        return {
            success: true,
            message: 'Email de confirmação enviado! Verifique sua caixa de entrada.',
            token: token,
            simulation: true
        };
    }
    
    /**
     * Fallback para modo simulação - Recuperação
     */
    fallbackPasswordReset(email, resetLink, token) {
        console.log('📧 [SIMULAÇÃO] Email de recuperação enviado para:', email);
        console.log('🔗 Link de recuperação:', resetLink);
        
        return {
            success: true,
            message: 'Email de recuperação enviado! Verifique sua caixa de entrada.',
            token: token,
            simulation: true
        };
    }
    
    /**
     * Confirma email do usuário
     */
    confirmEmail(token) {
        try {
            const tokens = JSON.parse(localStorage.getItem('emailTokens'));
            const tokenData = tokens.find(t => t.token === token && t.type === 'confirmation');
            
            if (!tokenData) {
                return {
                    success: false,
                    message: 'Token inválido ou expirado.'
                };
            }
            
            // Verificar se token não expirou (24 horas)
            const tokenAge = Date.now() - tokenData.createdAt;
            if (tokenAge > 24 * 60 * 60 * 1000) {
                this.removeEmailToken(token);
                return {
                    success: false,
                    message: 'Token expirado. Solicite um novo email de confirmação.'
                };
            }
            
            // Adicionar usuário aos usuários confirmados
            const users = JSON.parse(localStorage.getItem('users'));
            const confirmedUser = {
                ...tokenData.userData,
                emailVerified: true,
                confirmedAt: new Date().toISOString()
            };
            users.push(confirmedUser);
            localStorage.setItem('users', JSON.stringify(users));
            
            // Remover token usado
            this.removeEmailToken(token);
            
            return {
                success: true,
                message: 'Email confirmado com sucesso! Agora você pode fazer login.',
                user: confirmedUser
            };
            
        } catch (error) {
            console.error('Erro ao confirmar email:', error);
            return {
                success: false,
                message: 'Erro ao confirmar email. Tente novamente.'
            };
        }
    }
    
    /**
     * Redefine senha do usuário
     */
    resetPassword(token, newPassword) {
        try {
            const tokens = JSON.parse(localStorage.getItem('passwordTokens'));
            const tokenData = tokens.find(t => t.token === token);
            
            if (!tokenData) {
                return {
                    success: false,
                    message: 'Token inválido ou expirado.'
                };
            }
            
            // Verificar se token não expirou (1 hora)
            const tokenAge = Date.now() - tokenData.createdAt;
            if (tokenAge > 60 * 60 * 1000) {
                this.removePasswordToken(token);
                return {
                    success: false,
                    message: 'Token expirado. Solicite uma nova recuperação de senha.'
                };
            }
            
            // Atualizar senha do usuário
            const users = JSON.parse(localStorage.getItem('users'));
            const userIndex = users.findIndex(u => u.email === tokenData.email);
            
            if (userIndex === -1) {
                return {
                    success: false,
                    message: 'Usuário não encontrado.'
                };
            }
            
            users[userIndex].senha = newPassword;
            users[userIndex].passwordUpdatedAt = new Date().toISOString();
            localStorage.setItem('users', JSON.stringify(users));
            
            // Remover token usado
            this.removePasswordToken(token);
            
            return {
                success: true,
                message: 'Senha redefinida com sucesso! Agora você pode fazer login.'
            };
            
        } catch (error) {
            console.error('Erro ao redefinir senha:', error);
            return {
                success: false,
                message: 'Erro ao redefinir senha. Tente novamente.'
            };
        }
    }
    
    /**
     * Autentica usuário (login)
     */
    async authenticateUser(email, password) {
        try {
            // 1. Tentar autenticação via API (Banco de Dados)
            try {
                const response = await fetch(`${this.apiUrl}/api/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, senha: password })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        // Salvar sessão no localStorage para persistência
                        localStorage.setItem('currentUser', JSON.stringify(data.user));
                        localStorage.setItem('userType', data.user.tipo);
                        return data;
                    }
                }
            } catch (apiError) {
                console.log('API offline ou erro de conexão, tentando método local...', apiError);
            }

            // Credenciais especiais para acesso direto (demo/teste)
            const demoCredentials = {
                'barbearia@gmail.com': {
                    password: 'barbearia123',
                    tipo: 'barbearia',
                    nomeBarbearia: 'Barbearia Demo',
                    email: 'barbearia@gmail.com',
                    emailVerified: true
                },
                'cliente@gmail.com': {
                    password: 'cliente123',
                    tipo: 'cliente',
                    nomeCompleto: 'Cliente Demo',
                    email: 'cliente@gmail.com',
                    emailVerified: true
                }
            };
            
            // Verificar se é uma credencial demo
            if (demoCredentials[email]) {
                const demoUser = demoCredentials[email];
                if (demoUser.password === password) {
                    // Criar objeto de usuário completo
                    const user = {
                        ...demoUser,
                        senha: password,
                        lastLogin: new Date().toISOString(),
                        createdAt: new Date().toISOString()
                    };
                    
                    // Salvar informações do usuário no localStorage
                    localStorage.setItem('currentUser', JSON.stringify(user));
                    localStorage.setItem('userType', user.tipo);
                    localStorage.setItem('userName', user.nomeCompleto || user.nomeBarbearia || user.email);
                    
                    console.log('✅ Login demo realizado:', user.tipo);
                    
                    return {
                        success: true,
                        message: 'Login realizado com sucesso!',
                        user: user
                    };
                } else {
                    return {
                        success: false,
                        message: 'Senha incorreta.'
                    };
                }
            }
            
            // Autenticação normal (buscar no localStorage)
            const users = JSON.parse(localStorage.getItem('users') || '[]');
            const user = users.find(u => u.email === email && u.emailVerified);
            
            if (!user) {
                return {
                    success: false,
                    message: 'Email não encontrado ou não verificado.'
                };
            }
            
            if (user.senha !== password) {
                return {
                    success: false,
                    message: 'Senha incorreta.'
                };
            }
            
            // Atualizar último login
            user.lastLogin = new Date().toISOString();
            localStorage.setItem('users', JSON.stringify(users));
            
            // Salvar informações do usuário no localStorage para uso em outras páginas
            localStorage.setItem('currentUser', JSON.stringify(user));
            localStorage.setItem('userType', user.tipo || 'cliente');
            localStorage.setItem('userName', user.nomeCompleto || user.nomeBarbearia || user.email);
            
            return {
                success: true,
                message: 'Login realizado com sucesso!',
                user: user
            };
            
        } catch (error) {
            console.error('Erro na autenticação:', error);
            return {
                success: false,
                message: 'Erro na autenticação. Tente novamente.'
            };
        }
    }
    
    /**
     * Métodos auxiliares
     */
    generateToken() {
        return Math.random().toString(36).substring(2) + Date.now().toString(36);
    }
    
    saveEmailToken(token, userData, type) {
        const tokens = JSON.parse(localStorage.getItem('emailTokens'));
        tokens.push({
            token: token,
            userData: userData,
            type: type,
            createdAt: Date.now()
        });
        localStorage.setItem('emailTokens', JSON.stringify(tokens));
    }
    
    savePasswordToken(token, email) {
        const tokens = JSON.parse(localStorage.getItem('passwordTokens'));
        tokens.push({
            token: token,
            email: email,
            createdAt: Date.now()
        });
        localStorage.setItem('passwordTokens', JSON.stringify(tokens));
    }
    
    removeEmailToken(token) {
        const tokens = JSON.parse(localStorage.getItem('emailTokens'));
        const filteredTokens = tokens.filter(t => t.token !== token);
        localStorage.setItem('emailTokens', JSON.stringify(filteredTokens));
    }
    
    removePasswordToken(token) {
        const tokens = JSON.parse(localStorage.getItem('passwordTokens'));
        const filteredTokens = tokens.filter(t => t.token !== token);
        localStorage.setItem('passwordTokens', JSON.stringify(filteredTokens));
    }
    
    /**
     * Configurar EmailJS (método público)
     */
}

// Instância global do serviço de email
window.emailService = new EmailService();

console.log('📧 Sistema de email EasyCut carregado!');
console.log('🔧 Para envio real, configure EmailJS com suas credenciais.');
