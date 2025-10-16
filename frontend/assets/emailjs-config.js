/**
 * Configuração do EmailJS para o EasyCut
 * Este arquivo contém as configurações necessárias para o envio de emails
 */

// Configuração do EmailJS
const EMAILJS_CONFIG = {
    // Substitua pelos seus valores do EmailJS
    serviceId: 'service_easycut', // ID do serviço no EmailJS
    templateId: 'template_easycut', // ID do template no EmailJS
    publicKey: 'your_public_key_here', // Sua chave pública do EmailJS
    userId: 'your_user_id_here' // Seu User ID do EmailJS
};

// Inicializar EmailJS
if (typeof emailjs !== 'undefined') {
    emailjs.init(EMAILJS_CONFIG.publicKey);
}

// Exportar configuração para uso em outros arquivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EMAILJS_CONFIG;
} else if (typeof window !== 'undefined') {
    window.EMAILJS_CONFIG = EMAILJS_CONFIG;
}