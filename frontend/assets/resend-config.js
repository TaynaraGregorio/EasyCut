/**
 * CONFIGURAÇÃO RESEND - Alternativa Moderna
 * 
 * Resend é uma alternativa moderna ao SendGrid
 * Oferece 3.000 emails gratuitos por mês
 */

// 1. Criar conta em: https://resend.com/
// 2. Obter API Key gratuita
// 3. Configurar domínio (opcional para testes)

const RESEND_CONFIG = {
    apiKey: 're_xxxxxxxxxxxxx', // Sua API Key do Resend
    fromEmail: 'EasyCut <noreply@easycut.com>' // Seu email verificado
};

// Exemplo de uso com Resend:
async function sendEmailWithResend(userData, confirmationLink) {
    try {
        const response = await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${RESEND_CONFIG.apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                from: RESEND_CONFIG.fromEmail,
                to: [userData.email],
                subject: 'Confirme seu email - EasyCut',
                html: `
                    <h2>Olá, ${userData.name}!</h2>
                    <p>Obrigado por se cadastrar no EasyCut!</p>
                    <p>Clique no link abaixo para confirmar seu email:</p>
                    <a href="${confirmationLink}" style="background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Confirmar Email</a>
                    <p>Se o botão não funcionar, copie e cole o link:</p>
                    <p>${confirmationLink}</p>
                `
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error.message);
        }
        
        return {
            success: true,
            message: 'Email enviado com sucesso!',
            id: result.id
        };
        
    } catch (error) {
        console.error('Erro ao enviar email:', error);
        return {
            success: false,
            message: 'Erro ao enviar email: ' + error.message
        };
    }
}

console.log('📧 Configuração Resend carregada!');
console.log('🔗 Crie conta em: https://resend.com/');
console.log('🎁 3.000 emails gratuitos por mês!');








