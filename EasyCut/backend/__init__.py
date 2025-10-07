#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyCut - Backend Package
Sistema de validação para formulários de cadastro
"""

__version__ = "1.0.0"
__author__ = "EasyCut Team"

# Importar validadores principais
from .email_validator import EmailValidator
from .phone_validator import PhoneValidator
from .cpf_cnpj_validator import CPFCNPJValidator
from .form_validator import FormValidator

__all__ = [
    'EmailValidator',
    'PhoneValidator', 
    'CPFCNPJValidator',
    'FormValidator'
]

