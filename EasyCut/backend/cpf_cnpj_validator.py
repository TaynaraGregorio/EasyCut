#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Validador de CPF/CNPJ
Validação de CPF e CNPJ usando validação matemática (algoritmos oficiais)
"""

import re
from typing import Tuple, Dict, Any, List


class CPFCNPJValidator:
    """
    Classe para validação de CPF e CNPJ brasileiros
    """
    
    def __init__(self):
        # Regex para CPF
        self.cpf_regex = re.compile(r'^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$')
        
        # Regex para CNPJ
        self.cnpj_regex = re.compile(r'^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$')
        
        # CPFs inválidos conhecidos (todos os dígitos iguais)
        self.invalid_cpfs = {
            '00000000000', '11111111111', '22222222222', '33333333333',
            '44444444444', '55555555555', '66666666666', '77777777777',
            '88888888888', '99999999999'
        }
        
        # CNPJs inválidos conhecidos (todos os dígitos iguais)
        self.invalid_cnpjs = {
            '00000000000000', '11111111111111', '22222222222222', '33333333333333',
            '44444444444444', '55555555555555', '66666666666666', '77777777777777',
            '88888888888888', '99999999999999'
        }
    
    def clean_document(self, document: str) -> str:
        """
        Remove formatação do documento
        
        Args:
            document (str): CPF ou CNPJ com formatação
            
        Returns:
            str: Documento limpo apenas com dígitos
        """
        if not document:
            return ""
        
        # Remove todos os caracteres não numéricos
        cleaned = re.sub(r'\D', '', document)
        return cleaned
    
    def format_cpf(self, cpf: str) -> str:
        """
        Formata CPF no padrão brasileiro
        
        Args:
            cpf (str): CPF sem formatação
            
        Returns:
            str: CPF formatado (XXX.XXX.XXX-XX)
        """
        cleaned = self.clean_document(cpf)
        
        if len(cleaned) == 11:
            return f"{cleaned[:3]}.{cleaned[3:6]}.{cleaned[6:9]}-{cleaned[9:]}"
        
        return cpf
    
    def format_cnpj(self, cnpj: str) -> str:
        """
        Formata CNPJ no padrão brasileiro
        
        Args:
            cnpj (str): CNPJ sem formatação
            
        Returns:
            str: CNPJ formatado (XX.XXX.XXX/XXXX-XX)
        """
        cleaned = self.clean_document(cnpj)
        
        if len(cleaned) == 14:
            return f"{cleaned[:2]}.{cleaned[2:5]}.{cleaned[5:8]}/{cleaned[8:12]}-{cleaned[12:]}"
        
        return cnpj
    
    def validate_cpf_format(self, cpf: str) -> Tuple[bool, str]:
        """
        Valida formato básico do CPF usando regex
        
        Args:
            cpf (str): CPF para validar
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem)
        """
        if not cpf or not isinstance(cpf, str):
            return False, "CPF não pode estar vazio"
        
        cpf = cpf.strip()
        
        if not cpf:
            return False, "CPF não pode estar vazio"
        
        # Verificar formato com regex
        if not self.cpf_regex.match(cpf):
            return False, "Formato de CPF inválido"
        
        # Verificar se tem 11 dígitos
        cleaned = self.clean_document(cpf)
        if len(cleaned) != 11:
            return False, "CPF deve ter 11 dígitos"
        
        return True, "Formato válido"
    
    def validate_cnpj_format(self, cnpj: str) -> Tuple[bool, str]:
        """
        Valida formato básico do CNPJ usando regex
        
        Args:
            cnpj (str): CNPJ para validar
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem)
        """
        if not cnpj or not isinstance(cnpj, str):
            return False, "CNPJ não pode estar vazio"
        
        cnpj = cnpj.strip()
        
        if not cnpj:
            return False, "CNPJ não pode estar vazio"
        
        # Verificar formato com regex
        if not self.cnpj_regex.match(cnpj):
            return False, "Formato de CNPJ inválido"
        
        # Verificar se tem 14 dígitos
        cleaned = self.clean_document(cnpj)
        if len(cleaned) != 14:
            return False, "CNPJ deve ter 14 dígitos"
        
        return True, "Formato válido"
    
    def calculate_cpf_digits(self, cpf_digits: str) -> Tuple[int, int]:
        """
        Calcula os dígitos verificadores do CPF
        
        Args:
            cpf_digits (str): Primeiros 9 dígitos do CPF
            
        Returns:
            Tuple[int, int]: (primeiro_dígito, segundo_dígito)
        """
        # Primeiro dígito verificador
        sum1 = 0
        for i in range(9):
            sum1 += int(cpf_digits[i]) * (10 - i)
        
        remainder1 = sum1 % 11
        first_digit = 0 if remainder1 < 2 else 11 - remainder1
        
        # Segundo dígito verificador
        sum2 = 0
        for i in range(10):
            if i < 9:
                sum2 += int(cpf_digits[i]) * (11 - i)
            else:
                sum2 += first_digit * (11 - i)
        
        remainder2 = sum2 % 11
        second_digit = 0 if remainder2 < 2 else 11 - remainder2
        
        return first_digit, second_digit
    
    def calculate_cnpj_digits(self, cnpj_digits: str) -> Tuple[int, int]:
        """
        Calcula os dígitos verificadores do CNPJ
        
        Args:
            cnpj_digits (str): Primeiros 12 dígitos do CNPJ
            
        Returns:
            Tuple[int, int]: (primeiro_dígito, segundo_dígito)
        """
        # Primeiro dígito verificador
        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum1 = 0
        for i in range(12):
            sum1 += int(cnpj_digits[i]) * weights1[i]
        
        remainder1 = sum1 % 11
        first_digit = 0 if remainder1 < 2 else 11 - remainder1
        
        # Segundo dígito verificador
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum2 = 0
        for i in range(13):
            if i < 12:
                sum2 += int(cnpj_digits[i]) * weights2[i]
            else:
                sum2 += first_digit * weights2[i]
        
        remainder2 = sum2 % 11
        second_digit = 0 if remainder2 < 2 else 11 - remainder2
        
        return first_digit, second_digit
    
    def validate_cpf_math(self, cpf: str) -> Dict[str, Any]:
        """
        Valida CPF usando validação matemática
        
        Args:
            cpf (str): CPF para validar
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        result = {
            'is_valid': False,
            'cpf': cpf,
            'formatted_cpf': None,
            'error_message': None,
            'validation_details': {}
        }
        
        try:
            # Validar formato primeiro
            format_valid, format_msg = self.validate_cpf_format(cpf)
            if not format_valid:
                result['error_message'] = format_msg
                return result
            
            # Limpar CPF
            cleaned_cpf = self.clean_document(cpf)
            
            # Verificar se é um CPF inválido conhecido
            if cleaned_cpf in self.invalid_cpfs:
                result['error_message'] = "CPF inválido (todos os dígitos iguais)"
                return result
            
            # Separar dígitos base e verificadores
            base_digits = cleaned_cpf[:9]
            provided_digits = cleaned_cpf[9:]
            
            # Calcular dígitos verificadores corretos
            calculated_first, calculated_second = self.calculate_cpf_digits(base_digits)
            correct_digits = f"{calculated_first}{calculated_second}"
            
            # Verificar se os dígitos fornecidos são corretos
            if provided_digits == correct_digits:
                result['is_valid'] = True
                result['formatted_cpf'] = self.format_cpf(cleaned_cpf)
                result['validation_details'] = {
                    'base_digits': base_digits,
                    'calculated_digits': correct_digits,
                    'provided_digits': provided_digits,
                    'document_type': 'CPF'
                }
            else:
                result['error_message'] = f"CPF inválido. Dígitos verificadores incorretos"
                result['validation_details'] = {
                    'base_digits': base_digits,
                    'calculated_digits': correct_digits,
                    'provided_digits': provided_digits,
                    'document_type': 'CPF'
                }
                
        except Exception as e:
            result['error_message'] = f"Erro na validação: {str(e)}"
        
        return result
    
    def validate_cnpj_math(self, cnpj: str) -> Dict[str, Any]:
        """
        Valida CNPJ usando validação matemática
        
        Args:
            cnpj (str): CNPJ para validar
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        result = {
            'is_valid': False,
            'cnpj': cnpj,
            'formatted_cnpj': None,
            'error_message': None,
            'validation_details': {}
        }
        
        try:
            # Validar formato primeiro
            format_valid, format_msg = self.validate_cnpj_format(cnpj)
            if not format_valid:
                result['error_message'] = format_msg
                return result
            
            # Limpar CNPJ
            cleaned_cnpj = self.clean_document(cnpj)
            
            # Verificar se é um CNPJ inválido conhecido
            if cleaned_cnpj in self.invalid_cnpjs:
                result['error_message'] = "CNPJ inválido (todos os dígitos iguais)"
                return result
            
            # Separar dígitos base e verificadores
            base_digits = cleaned_cnpj[:12]
            provided_digits = cleaned_cnpj[12:]
            
            # Calcular dígitos verificadores corretos
            calculated_first, calculated_second = self.calculate_cnpj_digits(base_digits)
            correct_digits = f"{calculated_first}{calculated_second}"
            
            # Verificar se os dígitos fornecidos são corretos
            if provided_digits == correct_digits:
                result['is_valid'] = True
                result['formatted_cnpj'] = self.format_cnpj(cleaned_cnpj)
                result['validation_details'] = {
                    'base_digits': base_digits,
                    'calculated_digits': correct_digits,
                    'provided_digits': provided_digits,
                    'document_type': 'CNPJ'
                }
            else:
                result['error_message'] = f"CNPJ inválido. Dígitos verificadores incorretos"
                result['validation_details'] = {
                    'base_digits': base_digits,
                    'calculated_digits': correct_digits,
                    'provided_digits': provided_digits,
                    'document_type': 'CNPJ'
                }
                
        except Exception as e:
            result['error_message'] = f"Erro na validação: {str(e)}"
        
        return result
    
    def validate_document(self, document: str) -> Dict[str, Any]:
        """
        Valida CPF ou CNPJ automaticamente detectando o tipo
        
        Args:
            document (str): CPF ou CNPJ para validar
            
        Returns:
            Dict[str, Any]: Resultado da validação
        """
        cleaned = self.clean_document(document)
        
        if len(cleaned) == 11:
            return self.validate_cpf_math(document)
        elif len(cleaned) == 14:
            return self.validate_cnpj_math(document)
        else:
            return {
                'is_valid': False,
                'document': document,
                'error_message': 'Documento deve ter 11 dígitos (CPF) ou 14 dígitos (CNPJ)',
                'validation_details': {'document_type': 'UNKNOWN'}
            }
    
    def validate_document_for_form(self, document: str) -> Dict[str, Any]:
        """
        Validação específica para formulários web
        
        Args:
            document (str): CPF ou CNPJ
            
        Returns:
            Dict[str, Any]: Resultado formatado para uso em formulários
        """
        validation_result = self.validate_document(document)
        
        return {
            'is_valid': validation_result['is_valid'],
            'document': validation_result.get('cpf') or validation_result.get('cnpj') or validation_result.get('document'),
            'formatted_document': validation_result.get('formatted_cpf') or validation_result.get('formatted_cnpj'),
            'document_type': validation_result['validation_details'].get('document_type', 'UNKNOWN'),
            'message': validation_result['error_message'] or "Documento válido",
            'can_use': validation_result['is_valid']
        }
    
    def validate_multiple_documents(self, documents: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Valida múltiplos documentos
        
        Args:
            documents (List[str]): Lista de documentos para validar
            
        Returns:
            Dict[str, Dict[str, Any]]: Resultados para cada documento
        """
        results = {}
        
        for document in documents:
            if document:  # Ignora documentos vazios
                results[document] = self.validate_document_for_form(document)
        
        return results


def validate_cpf_simple(cpf: str) -> bool:
    """
    Função simples para validação rápida de CPF
    
    Args:
        cpf (str): CPF para validar
        
    Returns:
        bool: True se válido, False caso contrário
    """
    validator = CPFCNPJValidator()
    result = validator.validate_cpf_math(cpf)
    return result['is_valid']


def validate_cnpj_simple(cnpj: str) -> bool:
    """
    Função simples para validação rápida de CNPJ
    
    Args:
        cnpj (str): CNPJ para validar
        
    Returns:
        bool: True se válido, False caso contrário
    """
    validator = CPFCNPJValidator()
    result = validator.validate_cnpj_math(cnpj)
    return result['is_valid']


def validate_document_simple(document: str) -> bool:
    """
    Função simples para validação rápida de CPF ou CNPJ
    
    Args:
        document (str): CPF ou CNPJ para validar
        
    Returns:
        bool: True se válido, False caso contrário
    """
    validator = CPFCNPJValidator()
    result = validator.validate_document(document)
    return result['is_valid']


# Exemplo de uso e testes
if __name__ == "__main__":
    # Criar instância do validador
    validator = CPFCNPJValidator()
    
    # Lista de documentos para teste
    test_documents = [
        # CPFs válidos
        "11144477735",  # CPF válido
        "111.444.777-35",  # CPF válido formatado
        "12345678909",  # CPF válido
        "123.456.789-09",  # CPF válido formatado
        
        # CPFs inválidos
        "11144477734",  # CPF inválido (dígito errado)
        "11111111111",  # CPF inválido (todos iguais)
        "1234567890",   # CPF inválido (muito curto)
        "123456789012", # CPF inválido (muito longo)
        
        # CNPJs válidos
        "11222333000181",  # CNPJ válido
        "11.222.333/0001-81",  # CNPJ válido formatado
        "12345678000195",  # CNPJ válido
        "12.345.678/0001-95",  # CNPJ válido formatado
        
        # CNPJs inválidos
        "11222333000180",  # CNPJ inválido (dígito errado)
        "11111111111111",  # CNPJ inválido (todos iguais)
        "1234567800019",   # CNPJ inválido (muito curto)
        "123456780001951", # CNPJ inválido (muito longo)
        
        # Documentos inválidos
        "abc-def-ghi",     # Letras
        "",                # Vazio
        None               # Nulo
    ]
    
    print("=" * 70)
    print("TESTE DE VALIDAÇÃO DE CPF/CNPJ - EasyCut")
    print("=" * 70)
    
    for document in test_documents:
        print(f"\nTestando: '{document}'")
        print("-" * 50)
        
        # Validação completa
        if document:  # Só testa se não for vazio/nulo
            result = validator.validate_document_for_form(document)
            print(f"Validação completa: {'OK' if result['is_valid'] else 'ERRO'} - {result['message']}")
            
            if result['formatted_document']:
                print(f"Documento formatado: {result['formatted_document']}")
                print(f"Tipo: {result['document_type']}")
            
            if result['is_valid']:
                print("OK Documento válido!")
            else:
                print("ERRO Documento inválido")
        else:
            print("Validação completa: ERRO - Documento vazio")
    
    print("\n" + "=" * 70)
    print("TESTE DE MÚLTIPLOS DOCUMENTOS")
    print("=" * 70)
    
    # Teste com múltiplos documentos
    multiple_results = validator.validate_multiple_documents([
        "11144477735",
        "11.222.333/0001-81",
        "documento-invalido",
        "12345678909"
    ])
    
    for document, result in multiple_results.items():
        status = "OK VÁLIDO" if result['is_valid'] else "ERRO INVÁLIDO"
        print(f"{document}: {status} - {result['message']}")
        if result['document_type']:
            print(f"  Tipo: {result['document_type']}")
    
    print("\n" + "=" * 70)
    print("EXEMPLO DE USO EM FORMULÁRIO")
    print("=" * 70)
    
    # Simulação de validação em formulário
    def simulate_form_validation(document_input):
        result = validator.validate_document_for_form(document_input)
        
        if result['is_valid']:
            print(f"OK Documento '{document_input}' é válido!")
            print(f"  Formatado: {result['formatted_document']}")
            print(f"  Tipo: {result['document_type']}")
        else:
            print(f"ERRO Documento '{document_input}' é inválido: {result['message']}")
        
        return result['is_valid']
    
    # Teste com documentos do formulário
    form_documents = [
        "11144477735",
        "11.222.333/0001-81",
        "documento-invalido",
        "12345678909"
    ]
    
    for document in form_documents:
        simulate_form_validation(document)
        print()
    
    print("\n" + "=" * 70)
    print("ALGORITMOS DE VALIDAÇÃO")
    print("=" * 70)
    print("""
    ALGORITMOS IMPLEMENTADOS:
    
    CPF (11 dígitos):
    1. Primeiro dígito: Soma dos 9 primeiros × (10,9,8,7,6,5,4,3,2)
    2. Segundo dígito: Soma dos 10 primeiros × (11,10,9,8,7,6,5,4,3,2)
    3. Resto da divisão por 11
    4. Se resto < 2: dígito = 0, senão: dígito = 11 - resto
    
    CNPJ (14 dígitos):
    1. Primeiro dígito: Soma dos 12 primeiros × (5,4,3,2,9,8,7,6,5,4,3,2)
    2. Segundo dígito: Soma dos 13 primeiros × (6,5,4,3,2,9,8,7,6,5,4,3,2)
    3. Resto da divisão por 11
    4. Se resto < 2: dígito = 0, senão: dígito = 11 - resto
    
    OK VALIDAÇÕES INCLUÍDAS:
    - Formato com regex
    - Validação matemática
    - CPFs/CNPJs inválidos conhecidos
    - Formatação automática
    - Detecção automática de tipo
    """)
