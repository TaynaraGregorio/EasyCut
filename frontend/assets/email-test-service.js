/**
 * SERVIÇO DE EMAIL PARA TESTES - EasyCut
 * 
 * Esta versão usa EmailJS (gratuito) para envio real de emails
 * Sem necessidade de backend ou configuração complexa
 */

class EmailTestService {
    constructor() {
        // Configuração do EmailJS (gratuito)
        this.emailjsConfig = {
            serviceId: 'service_easycut', // Você precisa criar no EmailJS
            templateId: 'template_confirmation', // Template de confirmação
            userId: 'user_easycut' // Seu User ID do EmailJS
        };
        
        this.isEmailJSLoaded = false;
        this.initEmailJS();
    }
    
    async initEmailJS() {
        // Carregar EmailJS se disponível
        if (typeof emailjs !== 'undefined') {
            this.isEmailJSLoaded = true;
            emailjs.init(this.emailjsConfig.userId);
            console.log('📧 EmailJS carregado com sucesso!');
        } else {
            console.log('⚠️ EmailJS não encontrado. Usando modo simulação.');
        }
    }
    
    /**
     * Envia email de confirmação usando EmailJS
     */
    async sendConfirmationEmail(userData) {
        try {
            const token = this.generateToken();
            const confirmationLink = `${window.location.origin}/frontend/ConfirmarEmail.html?token=${token}&type=confirmation`;
            
            // Salvar dados temporariamente
            this.saveEmailToken(token, userData, 'confirmation');
            
            if (this.isEmailJSLoaded) {
                // Envio real com EmailJS
                const templateParams = {
                    to_email: userData.email,
                    to_name: userData.nomeCompleto || userData.nomeBarbearia || 'Usuário',
                    confirmation_link: confirmationLink,
                    from_name: 'EasyCut'
                };
                
                await emailjs.send(
                    this.emailjsConfig.serviceId,
                    this.emailjsConfig.templateId,
                    templateParams
                );
                
                console.log('✅ Email de confirmação enviado via EmailJS!');
            } else {
                // Modo simulação
                console.log('📧 [SIMULAÇÃO] Email de confirmação enviado para:', userData.email);
                console.log('🔗 Link de confirmação:', confirmationLink);
            }
            
            return {
                success: true,
                message: 'Email de confirmação enviado! Verifique sua caixa de entrada.',
                token: token
            };
            
        } catch (error) {
            console.error('Erro ao enviar email:', error);
            return {
                success: false,
                message: 'Erro ao enviar email. Usando modo simulação.',
                token: this.generateToken() // Fallback para teste
            };
        }
    }
    
    /**
     * Envia email de recuperação usando EmailJS
     */
    async sendPasswordResetEmail(email) {
        try {
            const users = JSON.parse(localStorage.getItem('users') || '[]');
            const user = users.find(u => u.email === email && u.emailVerified);
            
            if (!user) {
                return {
                    success: false,
                    message: 'Email não encontrado ou não verificado.'
                };
            }
            
            const token = this.generateToken();
            const resetLink = `${window.location.origin}/frontend/RedefinirSenha.html?token=${token}`;
            
            this.savePasswordToken(token, email);
            
            if (this.isEmailJSLoaded) {
                // Envio real com EmailJS
                const templateParams = {
                    to_email: email,
                    to_name: user.nomeCompleto || user.nomeBarbearia || 'Usuário',
                    reset_link: resetLink,
                    from_name: 'EasyCut'
                };
                
                await emailjs.send(
                    this.emailjsConfig.serviceId,
                    'template_password_reset', // Template de recuperação
                    templateParams
                );
                
                console.log('✅ Email de recuperação enviado via EmailJS!');
            } else {
                // Modo simulação
                console.log('📧 [SIMULAÇÃO] Email de recuperação enviado para:', email);
                console.log('🔗 Link de recuperação:', resetLink);
            }
            
            return {
                success: true,
                message: 'Email de recuperação enviado! Verifique sua caixa de entrada.',
                token: token
            };
            
        } catch (error) {
            console.error('Erro ao enviar email de recuperação:', error);
            return {
                success: false,
                message: 'Erro ao enviar email. Usando modo simulação.',
                token: this.generateToken() // Fallback para teste
            };
        }
    }
    
    // Métodos auxiliares (iguais ao email-service.js original)
    generateToken() {
        return Math.random().toString(36).substring(2) + Date.now().toString(36);
    }
    
    saveEmailToken(token, userData, type) {
        const tokens = JSON.parse(localStorage.getItem('emailTokens') || '[]');
        tokens.push({
            token: token,
            userData: userData,
            type: type,
            createdAt: Date.now()
        });
        localStorage.setItem('emailTokens', JSON.stringify(tokens));
    }
    
    savePasswordToken(token, email) {
        const tokens = JSON.parse(localStorage.getItem('passwordTokens') || '[]');
        tokens.push({
            token: token,
            email: email,
            createdAt: Date.now()
        });
        localStorage.setItem('passwordTokens', JSON.stringify(tokens));
    }
    
    // Métodos de confirmação e autenticação (iguais ao original)
    confirmEmail(token) {
        try {
            const tokens = JSON.parse(localStorage.getItem('emailTokens') || '[]');
            const tokenData = tokens.find(t => t.token === token && t.type === 'confirmation');
            
            if (!tokenData) {
                return {
                    success: false,
                    message: 'Token inválido ou expirado.'
                };
            }
            
            const tokenAge = Date.now() - tokenData.createdAt;
            if (tokenAge > 24 * 60 * 60 * 1000) {
                this.removeEmailToken(token);
                return {
                    success: false,
                    message: 'Token expirado. Solicite um novo email de confirmação.'
                };
            }
            
            const users = JSON.parse(localStorage.getItem('users') || '[]');
            const confirmedUser = {
                ...tokenData.userData,
                emailVerified: true,
                confirmedAt: new Date().toISOString()
            };
            users.push(confirmedUser);
            localStorage.setItem('users', JSON.stringify(users));
            
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
    
    authenticateUser(email, password) {
        try {
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
            
            user.lastLogin = new Date().toISOString();
            localStorage.setItem('users', JSON.stringify(users));
            
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
    
    resetPassword(token, newPassword) {
        try {
            const tokens = JSON.parse(localStorage.getItem('passwordTokens') || '[]');
            const tokenData = tokens.find(t => t.token === token);
            
            if (!tokenData) {
                return {
                    success: false,
                    message: 'Token inválido ou expirado.'
                };
            }
            
            const tokenAge = Date.now() - tokenData.createdAt;
            if (tokenAge > 60 * 60 * 1000) {
                this.removePasswordToken(token);
                return {
                    success: false,
                    message: 'Token expirado. Solicite uma nova recuperação de senha.'
                };
            }
            
            const users = JSON.parse(localStorage.getItem('users') || '[]');
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
    
    removeEmailToken(token) {
        const tokens = JSON.parse(localStorage.getItem('emailTokens') || '[]');
        const filteredTokens = tokens.filter(t => t.token !== token);
        localStorage.setItem('emailTokens', JSON.stringify(filteredTokens));
    }
    
    removePasswordToken(token) {
        const tokens = JSON.parse(localStorage.getItem('passwordTokens') || '[]');
        const filteredTokens = tokens.filter(t => t.token !== token);
        localStorage.setItem('passwordTokens', JSON.stringify(filteredTokens));
    }
}

// Instância global para testes
window.emailService = new EmailTestService();

console.log('🧪 Serviço de email para testes carregado!');
console.log('📧 Para envio real, configure EmailJS ou SMTP Gmail');








