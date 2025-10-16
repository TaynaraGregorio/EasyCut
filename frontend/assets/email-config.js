/**
 * CONFIGURAÇÃO RÁPIDA PARA TESTE DE EMAIL
 * 
 * Para testar o envio real de emails, siga estes passos:
 */

// 1. Configure suas credenciais do Gmail aqui:
const EMAIL_CONFIG = {
    // Substitua pelo seu email do Gmail
    user: 'easycutcontato@gmail.com',
    
    // Substitua pela senha de app do Gmail (não sua senha normal!)
    pass: 'sua-senha-de-app-de-16-caracteres',
    
    // Seu nome que aparecerá nos emails
    fromName: 'EasyCut'
};

// 2. Instruções para gerar senha de app:
/*
PASSOS PARA GERAR SENHA DE APP NO GMAIL:

1. Acesse: https://myaccount.google.com/
2. Vá em "Segurança" > "Verificação em duas etapas"
3. Ative a verificação em duas etapas (se não estiver ativa)
4. Em "Senhas de app", clique em "Gerar senha de app"
5. Escolha "Email" como aplicativo
6. Copie a senha de 16 caracteres gerada
7. Cole no campo 'pass' acima
*/

// 3. Para ativar envio real, descomente as linhas abaixo no email-service.js:
/*
// Descomente estas linhas no método sendConfirmationEmail():
const transporter = nodemailer.createTransporter(this.smtpConfig);
await transporter.sendMail({
    from: this.fromEmail,
    to: userData.email,
    subject: 'Confirme seu email - EasyCut',
    html: emailContent
});

// E também no método sendPasswordResetEmail():
const transporter = nodemailer.createTransporter(this.smtpConfig);
await transporter.sendMail({
    from: this.fromEmail,
    to: email,
    subject: 'Recuperação de senha - EasyCut',
    html: emailContent
});
*/

// 4. Instale o nodemailer (se estiver usando Node.js):
// npm install nodemailer

console.log('📧 Configuração de email carregada!');
console.log('🔧 Para ativar envio real, configure as credenciais acima');








