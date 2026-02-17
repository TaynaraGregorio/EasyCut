// EasyCut - Validação de CPF/CNPJ Frontend
// Validação de CPF e CNPJ brasileiros usando regex e validação matemática

class CPFCNPJValidatorFrontend {
    constructor() {
        // Regex para CPF
        this.cpfRegex = /^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$/;
        
        // Regex para CNPJ
        this.cnpjRegex = /^\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}$/;
        
        // CPFs inválidos conhecidos (todos os dígitos iguais)
        this.invalidCPFs = new Set([
            '00000000000', '11111111111', '22222222222', '33333333333',
            '44444444444', '55555555555', '66666666666', '77777777777',
            '88888888888', '99999999999'
        ]);
        
        // CNPJs inválidos conhecidos (todos os dígitos iguais)
        this.invalidCNPJs = new Set([
            '00000000000000', '11111111111111', '22222222222222', '33333333333333',
            '44444444444444', '55555555555555', '66666666666666', '77777777777777',
            '88888888888888', '99999999999999'
        ]);
    }

    /**
     * Remove formatação do documento
     * @param {string} document - CPF ou CNPJ
     * @returns {string} - Documento limpo apenas com dígitos
     */
    cleanDocument(document) {
        if (!document) return '';
        return document.replace(/\D/g, '');
    }

    /**
     * Formata CPF no padrão brasileiro
     * @param {string} cpf - CPF sem formatação
     * @returns {string} - CPF formatado (XXX.XXX.XXX-XX)
     */
    formatCPF(cpf) {
        const cleaned = this.cleanDocument(cpf);
        
        if (cleaned.length === 11) {
            return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        }
        
        return cpf;
    }

    /**
     * Formata CNPJ no padrão brasileiro
     * @param {string} cnpj - CNPJ sem formatação
     * @returns {string} - CNPJ formatado (XX.XXX.XXX/XXXX-XX)
     */
    formatCNPJ(cnpj) {
        const cleaned = this.cleanDocument(cnpj);
        
        if (cleaned.length === 14) {
            return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
        }
        
        return cnpj;
    }

    /**
     * Formata documento automaticamente (CPF ou CNPJ)
     * @param {string} document - Documento sem formatação
     * @returns {string} - Documento formatado
     */
    formatDocument(document) {
        const cleaned = this.cleanDocument(document);
        
        if (cleaned.length === 11) {
            return this.formatCPF(cleaned);
        } else if (cleaned.length === 14) {
            return this.formatCNPJ(cleaned);
        }
        
        return document;
    }

    /**
     * Calcula os dígitos verificadores do CPF
     * @param {string} cpfDigits - Primeiros 9 dígitos do CPF
     * @returns {Array<number>} - [primeiro_dígito, segundo_dígito]
     */
    calculateCPFDigits(cpfDigits) {
        // Primeiro dígito verificador
        let sum1 = 0;
        for (let i = 0; i < 9; i++) {
            sum1 += parseInt(cpfDigits[i]) * (10 - i);
        }
        
        let remainder1 = sum1 % 11;
        let firstDigit = remainder1 < 2 ? 0 : 11 - remainder1;
        
        // Segundo dígito verificador
        let sum2 = 0;
        for (let i = 0; i < 10; i++) {
            if (i < 9) {
                sum2 += parseInt(cpfDigits[i]) * (11 - i);
            } else {
                sum2 += firstDigit * (11 - i);
            }
        }
        
        let remainder2 = sum2 % 11;
        let secondDigit = remainder2 < 2 ? 0 : 11 - remainder2;
        
        return [firstDigit, secondDigit];
    }

    /**
     * Calcula os dígitos verificadores do CNPJ
     * @param {string} cnpjDigits - Primeiros 12 dígitos do CNPJ
     * @returns {Array<number>} - [primeiro_dígito, segundo_dígito]
     */
    calculateCNPJDigits(cnpjDigits) {
        // Primeiro dígito verificador
        const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        let sum1 = 0;
        for (let i = 0; i < 12; i++) {
            sum1 += parseInt(cnpjDigits[i]) * weights1[i];
        }
        
        let remainder1 = sum1 % 11;
        let firstDigit = remainder1 < 2 ? 0 : 11 - remainder1;
        
        // Segundo dígito verificador
        const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        let sum2 = 0;
        for (let i = 0; i < 13; i++) {
            if (i < 12) {
                sum2 += parseInt(cnpjDigits[i]) * weights2[i];
            } else {
                sum2 += firstDigit * weights2[i];
            }
        }
        
        let remainder2 = sum2 % 11;
        let secondDigit = remainder2 < 2 ? 0 : 11 - remainder2;
        
        return [firstDigit, secondDigit];
    }

    /**
     * Valida formato básico do CPF usando regex
     * @param {string} cpf - CPF para validar
     * @returns {Object} - {isValid: boolean, message: string}
     */
    validateCPFFormat(cpf) {
        if (!cpf || typeof cpf !== 'string') {
            return { isValid: false, message: 'CPF não pode estar vazio' };
        }

        const trimmed = cpf.trim();
        if (!trimmed) {
            return { isValid: false, message: 'CPF não pode estar vazio' };
        }

        // Verificar formato com regex
        if (!this.cpfRegex.test(trimmed)) {
            return { isValid: false, message: 'Formato de CPF inválido' };
        }

        // Verificar se tem 11 dígitos
        const cleaned = this.cleanDocument(trimmed);
        if (cleaned.length !== 11) {
            return { isValid: false, message: 'CPF deve ter 11 dígitos' };
        }

        return { isValid: true, message: 'Formato válido' };
    }

    /**
     * Valida formato básico do CNPJ usando regex
     * @param {string} cnpj - CNPJ para validar
     * @returns {Object} - {isValid: boolean, message: string}
     */
    validateCNPJFormat(cnpj) {
        if (!cnpj || typeof cnpj !== 'string') {
            return { isValid: false, message: 'CNPJ não pode estar vazio' };
        }

        const trimmed = cnpj.trim();
        if (!trimmed) {
            return { isValid: false, message: 'CNPJ não pode estar vazio' };
        }

        // Verificar formato com regex
        if (!this.cnpjRegex.test(trimmed)) {
            return { isValid: false, message: 'Formato de CNPJ inválido' };
        }

        // Verificar se tem 14 dígitos
        const cleaned = this.cleanDocument(trimmed);
        if (cleaned.length !== 14) {
            return { isValid: false, message: 'CNPJ deve ter 14 dígitos' };
        }

        return { isValid: true, message: 'Formato válido' };
    }

    /**
     * Valida CPF usando validação matemática
     * @param {string} cpf - CPF para validar
     * @returns {Object} - Resultado da validação
     */
    validateCPFMath(cpf) {
        const result = {
            isValid: false,
            cpf: cpf,
            formattedCPF: null,
            message: null,
            documentType: 'CPF'
        };

        try {
            // Validar formato primeiro
            const formatResult = this.validateCPFFormat(cpf);
            if (!formatResult.isValid) {
                result.message = formatResult.message;
                return result;
            }

            // Limpar CPF
            const cleanedCPF = this.cleanDocument(cpf);

            // Verificar se é um CPF inválido conhecido
            if (this.invalidCPFs.has(cleanedCPF)) {
                result.message = 'CPF inválido (todos os dígitos iguais)';
                return result;
            }

            // Separar dígitos base e verificadores
            const baseDigits = cleanedCPF.substring(0, 9);
            const providedDigits = cleanedCPF.substring(9);

            // Calcular dígitos verificadores corretos
            const [calculatedFirst, calculatedSecond] = this.calculateCPFDigits(baseDigits);
            const correctDigits = `${calculatedFirst}${calculatedSecond}`;

            // Verificar se os dígitos fornecidos são corretos
            if (providedDigits === correctDigits) {
                result.isValid = true;
                result.formattedCPF = this.formatCPF(cleanedCPF);
                result.message = 'CPF válido';
            } else {
                result.message = 'CPF inválido. Dígitos verificadores incorretos';
            }

        } catch (error) {
            result.message = `Erro na validação: ${error.message}`;
        }

        return result;
    }

    /**
     * Valida CNPJ usando validação matemática
     * @param {string} cnpj - CNPJ para validar
     * @returns {Object} - Resultado da validação
     */
    validateCNPJMath(cnpj) {
        const result = {
            isValid: false,
            cnpj: cnpj,
            formattedCNPJ: null,
            message: null,
            documentType: 'CNPJ'
        };

        try {
            // Validar formato primeiro
            const formatResult = this.validateCNPJFormat(cnpj);
            if (!formatResult.isValid) {
                result.message = formatResult.message;
                return result;
            }

            // Limpar CNPJ
            const cleanedCNPJ = this.cleanDocument(cnpj);

            // Verificar se é um CNPJ inválido conhecido
            if (this.invalidCNPJs.has(cleanedCNPJ)) {
                result.message = 'CNPJ inválido (todos os dígitos iguais)';
                return result;
            }

            // Separar dígitos base e verificadores
            const baseDigits = cleanedCNPJ.substring(0, 12);
            const providedDigits = cleanedCNPJ.substring(12);

            // Calcular dígitos verificadores corretos
            const [calculatedFirst, calculatedSecond] = this.calculateCNPJDigits(baseDigits);
            const correctDigits = `${calculatedFirst}${calculatedSecond}`;

            // Verificar se os dígitos fornecidos são corretos
            if (providedDigits === correctDigits) {
                result.isValid = true;
                result.formattedCNPJ = this.formatCNPJ(cleanedCNPJ);
                result.message = 'CNPJ válido';
            } else {
                result.message = 'CNPJ inválido. Dígitos verificadores incorretos';
            }

        } catch (error) {
            result.message = `Erro na validação: ${error.message}`;
        }

        return result;
    }

    /**
     * Valida CPF ou CNPJ automaticamente detectando o tipo
     * @param {string} document - CPF ou CNPJ para validar
     * @returns {Object} - Resultado da validação
     */
    validateDocument(document) {
        const cleaned = this.cleanDocument(document);

        if (cleaned.length === 11) {
            return this.validateCPFMath(document);
        } else if (cleaned.length === 14) {
            return this.validateCNPJMath(document);
        } else {
            return {
                isValid: false,
                document: document,
                message: 'Documento deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)',
                documentType: 'UNKNOWN'
            };
        }
    }

    /**
     * Validação específica para formulários web
     * @param {string} document - CPF ou CNPJ
     * @returns {Object} - Resultado formatado para uso em formulários
     */
    validateForForm(document) {
        const validationResult = this.validateDocument(document);

        return {
            isValid: validationResult.isValid,
            document: validationResult.document,
            formattedDocument: validationResult.formattedCPF || validationResult.formattedCNPJ,
            documentType: validationResult.documentType,
            message: validationResult.message,
            canUse: validationResult.isValid
        };
    }

    /**
     * Determina o tipo de documento baseado no tamanho
     * @param {string} document - Documento para analisar
     * @returns {string} - Tipo do documento
     */
    getDocumentType(document) {
        const cleaned = this.cleanDocument(document);

        if (cleaned.length === 11) {
            return 'CPF';
        } else if (cleaned.length === 14) {
            return 'CNPJ';
        }

        return 'UNKNOWN';
    }
}

// Instância global do validador
const cpfCnpjValidator = new CPFCNPJValidatorFrontend();

// Funções utilitárias para uso direto
function formatCPFCNPJInput(input) {
    const formatted = cpfCnpjValidator.formatDocument(input.value);
    input.value = formatted;
}

function validateCPFCNPJInput(input) {
    const result = cpfCnpjValidator.validateForForm(input.value);

    // Aplicar estilos visuais
    if (result.isValid) {
        input.style.borderColor = '#10b981';
        input.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.1)';
    } else {
        input.style.borderColor = '#ef4444';
        input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)';
    }

    // Mostrar/ocultar mensagem de erro
    showCPFCNPJValidationMessage(input, result);

    return result;
}

function showCPFCNPJValidationMessage(input, result) {
    // Remove mensagem anterior
    const existingMsg = input.parentNode.querySelector('.cpf-cnpj-validation-message');
    if (existingMsg) {
        existingMsg.remove();
    }

    if (!result.isValid) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'cpf-cnpj-validation-message';
        errorMsg.style.cssText = 'color: #ef4444; font-size: 0.85rem; margin-top: 4px;';
        errorMsg.textContent = result.message;
        input.parentNode.appendChild(errorMsg);
    }
}

// Event listeners para formatação automática
function setupCPFCNPJValidation(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Formatação em tempo real
    input.addEventListener('input', function(e) {
        formatCPFCNPJInput(e.target);
    });

    // Validação ao sair do campo
    input.addEventListener('blur', function(e) {
        validateCPFCNPJInput(e.target);
    });

    // Validação ao focar (limpar estilos)
    input.addEventListener('focus', function(e) {
        e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        e.target.style.boxShadow = 'none';

        const existingMsg = e.target.parentNode.querySelector('.cpf-cnpj-validation-message');
        if (existingMsg) existingMsg.remove();
    });
}

// Função para validar múltiplos documentos
function validateMultipleDocuments(documentInputs) {
    const results = {};

    documentInputs.forEach(input => {
        if (input.value.trim()) {
            results[input.id] = cpfCnpjValidator.validateForForm(input.value);
        }
    });

    return results;
}

// Exemplo de uso e testes
if (typeof window !== 'undefined') {
    // Executar testes quando carregado no navegador
    document.addEventListener('DOMContentLoaded', function() {
        console.log('EasyCut - Validador de CPF/CNPJ Frontend carregado');

        // Configurar validação automática para campos de CPF/CNPJ
        const documentInputs = document.querySelectorAll('input[name*="cpf"], input[name*="cnpj"], input[name*="cnpjCpf"]');
        documentInputs.forEach(input => {
            setupCPFCNPJValidation(input.id);
        });

        // Exemplo de teste
        const testDocuments = [
            '11144477735',
            '111.444.777-35',
            '11222333000181',
            '11.222.333/0001-81',
            'documento-invalido'
        ];

        console.log('Testando validação de documentos:');
        testDocuments.forEach(document => {
            const result = cpfCnpjValidator.validateForForm(document);
            console.log(`${document}: ${result.isValid ? '✓' : '✗'} - ${result.message}`);
        });
    });
}
