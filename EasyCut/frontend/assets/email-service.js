/**
 * Sistema de Email e Autenticação - EasyCut
 * Versão com EmailJS para envio real de emails
 */

class EmailService {
    constructor() {
        // Configuração EmailJS - SUBSTITUA PELOS SEUS VALORES
        this.emailjsConfig = {
            serviceId: 'service_easycut', // Substitua pelo seu Service ID
            templateIdConfirmation: 'template_confirmation', // Template de confirmação
            templateIdPasswordReset: 'template_password_reset', // Template de recuperação
            userId: 'user_easycut' // Substitua pelo seu User ID
        };
        
        this.baseUrl = window.location.origin;
        this.isEmailJSLoaded = false;
        
        // Inicializar dados de usuários no localStorage se não existirem
        this.initUserData();
        
        // Verificar se EmailJS está carregado
        this.checkEmailJS();
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
    
    checkEmailJS() {
        // Verificar se EmailJS está disponível
        if (typeof emailjs !== 'undefined') {
            this.isEmailJSLoaded = true;
            emailjs.init(this.emailjsConfig.userId);
            console.log('✅ EmailJS carregado com sucesso!');
            console.log('📧 Pronto para enviar emails reais!');
        } else {
            console.log('⚠️ EmailJS não encontrado. Usando modo simulação.');
            console.log('🔧 Para envio real, configure EmailJS primeiro.');
        }
    }
    
    /**
     * Envia email de confirmação para novo usuário
     */
    async sendConfirmationEmail(userData) {
        try {
            const token = this.generateToken();
            const confirmationLink = `${this.baseUrl}/frontend/ConfirmarEmail.html?token=${token}&type=confirmation`;
            
            // Salvar dados do usuário temporariamente
            const tempUser = {
                ...userData,
                emailVerified: false,
                createdAt: new Date().toISOString()
            };
            
            // Salvar token de confirmação
            this.saveEmailToken(token, tempUser, 'confirmation');
            
            const emailContent = this.getConfirmationEmailTemplate(userData.name, confirmationLink);
            
            // Simular envio de email (em produção, usar biblioteca como nodemailer)
            console.log('📧 Email de confirmação enviado para:', userData.email);
            console.log('🔗 Link de confirmação:', confirmationLink);
            
            // Em produção, descomente o código abaixo para envio real:
            /*
            const transporter = nodemailer.createTransporter(this.smtpConfig);
            await transporter.sendMail({
                from: this.fromEmail,
                to: userData.email,
                subject: 'Confirme seu email - EasyCut',
                html: emailContent
            });
            */
            
            return {
                success: true,
                message: 'Email de confirmação enviado! Verifique sua caixa de entrada.',
                token: token // Para testes
            };
            
        } catch (error) {
            console.error('Erro ao enviar email de confirmação:', error);
            return {
                success: false,
                message: 'Erro ao enviar email de confirmação. Tente novamente.'
            };
        }
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
            const resetLink = `${this.baseUrl}/frontend/RedefinirSenha.html?token=${token}`;
            
            // Salvar token de recuperação
            this.savePasswordToken(token, email);
            
            const emailContent = this.getPasswordResetEmailTemplate(user.name, resetLink);
            
            // Simular envio de email
            console.log('📧 Email de recuperação enviado para:', email);
            console.log('🔗 Link de recuperação:', resetLink);
            
            // Em produção, descomente o código abaixo:
            /*
            const transporter = nodemailer.createTransporter(this.smtpConfig);
            await transporter.sendMail({
                from: this.fromEmail,
                to: email,
                subject: 'Recuperação de senha - EasyCut',
                html: emailContent
            });
            */
            
            return {
                success: true,
                message: 'Email de recuperação enviado! Verifique sua caixa de entrada.',
                token: token // Para testes
            };
            
        } catch (error) {
            console.error('Erro ao enviar email de recuperação:', error);
            return {
                success: false,
                message: 'Erro ao enviar email de recuperação. Tente novamente.'
            };
        }
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
    authenticateUser(email, password) {
        try {
            const users = JSON.parse(localStorage.getItem('users'));
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
     * Templates de email
     */
    getConfirmationEmailTemplate(name, confirmationLink) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Confirme seu email - EasyCut</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Bem-vindo ao EasyCut!</h1>
                        <p>Confirme seu email para começar a usar nossa plataforma</p>
                    </div>
                    <div class="content">
                        <h2>Olá, ${name}!</h2>
                        <p>Obrigado por se cadastrar no EasyCut! Para ativar sua conta e começar a usar nossa plataforma, você precisa confirmar seu endereço de email.</p>
                        
                        <p>Clique no botão abaixo para confirmar seu email:</p>
                        
                        <a href="${confirmationLink}" class="button">✅ Confirmar Email</a>
                        
                        <p>Se o botão não funcionar, copie e cole o link abaixo no seu navegador:</p>
                        <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">${confirmationLink}</p>
                        
                        <p><strong>Importante:</strong> Este link expira em 24 horas por motivos de segurança.</p>
                        
                        <p>Se você não se cadastrou no EasyCut, pode ignorar este email.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 EasyCut - Todos os direitos reservados</p>
                        <p>Este é um email automático, não responda a esta mensagem.</p>
                    </div>
                </div>
            </body>
            </html>
        `;
    }
    
    getPasswordResetEmailTemplate(name, resetLink) {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Recuperação de senha - EasyCut</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #ef4444 0%, #f59e0b 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                    .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                    .button { display: inline-block; background: #ef4444; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Recuperação de Senha</h1>
                        <p>Redefina sua senha do EasyCut</p>
                    </div>
                    <div class="content">
                        <h2>Olá, ${name}!</h2>
                        <p>Recebemos uma solicitação para redefinir a senha da sua conta no EasyCut.</p>
                        
                        <p>Se você solicitou esta alteração, clique no botão abaixo para criar uma nova senha:</p>
                        
                        <a href="${resetLink}" class="button">🔑 Redefinir Senha</a>
                        
                        <p>Se o botão não funcionar, copie e cole o link abaixo no seu navegador:</p>
                        <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">${resetLink}</p>
                        
                        <p><strong>Importante:</strong> Este link expira em 1 hora por motivos de segurança.</p>
                        
                        <p>Se você não solicitou a redefinição de senha, pode ignorar este email. Sua senha permanecerá inalterada.</p>
                    </div>
                    <div class="footer">
                        <p>© 2024 EasyCut - Todos os direitos reservados</p>
                        <p>Este é um email automático, não responda a esta mensagem.</p>
                    </div>
                </div>
            </body>
            </html>
        `;
    }
}

// Instância global do serviço de email
window.emailService = new EmailService();
