// EasyCut - Validação de Telefone Frontend
// Validação de números de telefone brasileiros usando regex

class PhoneValidatorFrontend {
    constructor() {
        // Regex para telefones brasileiros
        this.phoneRegex = /^(\+55\s?)?(\(?[1-9]{2}\)?)\s?([0-9]{4,5})\-?([0-9]{4})$/;
        
        // Regex para celular brasileiro (9 dígitos)
        this.cellRegex = /^(\+55\s?)?(\(?[1-9]{2}\)?)\s?([0-9]{5})\-?([0-9]{4})$/;
        
        // DDDs válidos do Brasil
        this.validDDDs = [
            '11', '12', '13', '14', '15', '16', '17', '18', '19', // SP
            '21', '22', '24', // RJ
            '27', '28', // ES
            '31', '32', '33', '34', '35', '37', '38', // MG
            '41', '42', '43', '44', '45', '46', // PR
            '47', '48', '49', // SC
            '51', '53', '54', '55', // RS
            '61', // DF
            '62', '64', // GO
            '63', // TO
            '65', '66', // MT
            '67', // MS
            '68', // AC
            '69', // RO
            '71', '73', '74', '75', '77', // BA
            '79', // SE
            '81', '87', // PE
            '82', // AL
            '83', // PB
            '84', // RN
            '85', '88', // CE
            '86', '89', // PI
            '91', '93', '94', // PA
            '92', '97', // AM
            '95', // RR
            '96', // AP
            '98', '99' // MA
        ];
    }

    /**
     * Remove formatação do número de telefone
     * @param {string} phone - Número de telefone
     * @returns {string} - Número limpo apenas com dígitos
     */
    cleanPhone(phone) {
        if (!phone) return '';
        return phone.replace(/\D/g, '');
    }

    /**
     * Formata número de telefone brasileiro
     * @param {string} phone - Número de telefone
     * @returns {string} - Número formatado
     */
    formatPhone(phone) {
        const cleaned = this.cleanPhone(phone);
        
        if (cleaned.length === 0) return '';
        
        // Remove código do país se presente
        let number = cleaned;
        if (number.startsWith('55') && number.length > 11) {
            number = number.substring(2);
        }
        
        // Formata conforme o tamanho (apenas celulares)
        if (number.length === 11) {
            // Celular: (XX) XXXXX-XXXX
            return number.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        }
        
        return phone; // Retorna original se não conseguir formatar
    }

    /**
     * Valida formato básico do telefone
     * @param {string} phone - Número de telefone
     * @returns {Object} - {isValid: boolean, message: string}
     */
    validateFormat(phone) {
        if (!phone || typeof phone !== 'string') {
            return { isValid: false, message: 'Telefone não pode estar vazio' };
        }

        const trimmed = phone.trim();
        if (!trimmed) {
            return { isValid: false, message: 'Telefone não pode estar vazio' };
        }

        const cleaned = this.cleanPhone(trimmed);
        
        // Verificar tamanho mínimo
        if (cleaned.length < 10) {
            return { isValid: false, message: 'Telefone deve ter pelo menos 10 dígitos' };
        }

        // Verificar tamanho máximo
        if (cleaned.length > 13) {
            return { isValid: false, message: 'Telefone tem muitos dígitos' };
        }

        // Verificar formato brasileiro
        if (!this.phoneRegex.test(trimmed) && !trimmed.startsWith('+55')) {
            return { isValid: false, message: 'Formato de telefone inválido para o Brasil' };
        }

        // Extrair DDD
        let ddd = '';
        if (cleaned.startsWith('55') && cleaned.length > 11) {
            ddd = cleaned.substring(2, 4);
        } else {
            ddd = cleaned.substring(0, 2);
        }

        // Verificar se DDD é válido
        if (!this.validDDDs.includes(ddd)) {
            return { isValid: false, message: `DDD ${ddd} não é válido para o Brasil` };
        }

        return { isValid: true, message: 'Formato válido' };
    }

    /**
     * Determina o tipo de telefone
     * @param {string} phone - Número de telefone
     * @returns {string} - Tipo do telefone
     */
    getPhoneType(phone) {
        const cleaned = this.cleanPhone(phone);
        
        if (cleaned.length === 11) {
            return 'Celular';
        }
        
        return 'Desconhecido';
    }

    /**
     * Validação completa para formulários
     * @param {string} phone - Número de telefone
     * @returns {Object} - Resultado da validação
     */
    validateForForm(phone) {
        const formatResult = this.validateFormat(phone);
        
        return {
            isValid: formatResult.isValid,
            phone: phone,
            formattedPhone: formatResult.isValid ? this.formatPhone(phone) : phone,
            phoneType: formatResult.isValid ? this.getPhoneType(phone) : 'Desconhecido',
            message: formatResult.message,
            canUse: formatResult.isValid
        };
    }

    /**
     * Formata número para WhatsApp
     * @param {string} phone - Número de telefone
     * @returns {string} - Número formatado para WhatsApp
     */
    getWhatsAppFormat(phone) {
        const cleaned = this.cleanPhone(phone);
        
        if (!cleaned) return '';
        
        // Adicionar código do país se necessário
        let whatsappNumber = cleaned;
        if (!whatsappNumber.startsWith('55')) {
            whatsappNumber = '55' + whatsappNumber;
        }
        
        return '+' + whatsappNumber;
    }
}

// Instância global do validador
const phoneValidator = new PhoneValidatorFrontend();

// Funções utilitárias para uso direto
function formatPhoneInput(input) {
    const formatted = phoneValidator.formatPhone(input.value);
    input.value = formatted;
}

function validatePhoneInput(input) {
    const result = phoneValidator.validateForForm(input.value);
    
    // Aplicar estilos visuais
    if (result.isValid) {
        input.style.borderColor = '#10b981';
        input.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
    } else {
        input.style.borderColor = '#ef4444';
        input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    }
    
    // Mostrar/ocultar mensagem de erro
    showPhoneValidationMessage(input, result);
    
    return result;
}

function showPhoneValidationMessage(input, result) {
    // Remove mensagem anterior
    const existingMsg = input.parentNode.querySelector('.phone-validation-message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    if (!result.isValid) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'phone-validation-message';
        errorMsg.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 4px;';
        errorMsg.textContent = result.message;
        input.parentNode.appendChild(errorMsg);
    }
}

// Event listeners para formatação automática
function setupPhoneValidation(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Formatação em tempo real
    input.addEventListener('input', function(e) {
        formatPhoneInput(e.target);
    });
    
    // Validação ao sair do campo
    input.addEventListener('blur', function(e) {
        validatePhoneInput(e.target);
    });
    
    // Validação ao focar (limpar estilos)
    input.addEventListener('focus', function(e) {
        e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        e.target.style.boxShadow = 'none';
        
        const existingMsg = e.target.parentNode.querySelector('.phone-validation-message');
        if (existingMsg) existingMsg.remove();
    });
}

// Função para validar múltiplos telefones
function validateMultiplePhones(phoneInputs) {
    const results = {};
    
    phoneInputs.forEach(input => {
        if (input.value.trim()) {
            results[input.id] = phoneValidator.validateForForm(input.value);
        }
    });
    
    return results;
}

// Exemplo de uso e testes
if (typeof window !== 'undefined') {
    // Executar testes quando carregado no navegador
    document.addEventListener('DOMContentLoaded', function() {
        console.log('EasyCut - Validador de Telefone Frontend carregado');
        
        // Configurar validação automática para campos de telefone
        const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="telefone"], input[name*="whatsapp"]');
        phoneInputs.forEach(input => {
            setupPhoneValidation(input.id);
        });
        
        // Exemplo de teste
        const testPhones = [
            '(11) 99999-9999',
            '11999999999',
            '+55 11 99999-9999',
            'telefone-invalido'
        ];
        
        console.log('Testando validação de telefones:');
        testPhones.forEach(phone => {
            const result = phoneValidator.validateForForm(phone);
            console.log(`${phone}: ${result.isValid ? '✓' : '✗'} - ${result.message}`);
        });
    });
}
