# 🚀 CONFIGURAÇÃO RÁPIDA - EMAIL REAL

## ⚡ Passos para Ativar Envio Real (5 minutos)

### 1️⃣ **Criar Conta EmailJS**
- Acesse: https://www.emailjs.com/
- Clique em "Sign Up" (gratuito)
- Confirme seu email

### 2️⃣ **Conectar Gmail**
- No dashboard: "Email Services" → "Add New Service"
- Escolha "Gmail" e faça login
- **Anote o Service ID** (ex: `service_abc123`)

### 3️⃣ **Criar Templates**

#### Template 1: Confirmação
- "Email Templates" → "Create New Template"
- **Template ID**: `template_confirmation`
- **Subject**: `Confirme seu email - EasyCut`
- **Content**:
```
Olá {{to_name}},

Obrigado por se cadastrar no EasyCut!

Clique no link abaixo para confirmar seu email:
{{confirmation_link}}

Este link expira em 24 horas.

Equipe EasyCut
```

#### Template 2: Recuperação
- **Template ID**: `template_password_reset`
- **Subject**: `Recuperação de senha - EasyCut`
- **Content**:
```
Olá {{to_name}},

Você solicitou a recuperação de senha.

Clique no link abaixo para redefinir sua senha:
{{reset_link}}

Este link expira em 1 hora.

Equipe EasyCut
```

### 4️⃣ **Obter User ID**
- "Account" → "General"
- Copie seu **Public Key (User ID)** (ex: `user_xyz789`)

### 5️⃣ **Atualizar Código**
No arquivo `frontend/assets/emailjs-config.js`, substitua:

```javascript
const EMAILJS_CONFIG = {
    serviceId: 'service_abc123', // Seu Service ID
    templateIdConfirmation: 'template_confirmation',
    templateIdPasswordReset: 'template_password_reset',
    userId: 'user_xyz789' // Seu User ID
};
```

### 6️⃣ **Testar**
1. Cadastre um usuário
2. **Email chegará de verdade!** 📧
3. Confirme o email
4. Faça login

---

## ✅ **Pronto!**

- ✅ **200 emails/mês gratuitos**
- ✅ **Sem backend necessário**
- ✅ **Emails chegam normalmente**
- ✅ **Configuração em 5 minutos**

---

## 🔧 **Arquivos Atualizados**

- ✅ `email-service-real.js` - Serviço com EmailJS
- ✅ `emailjs-config.js` - Configuração automática
- ✅ Todas as páginas atualizadas
- ✅ Scripts EmailJS incluídos

---

## 🆘 **Problemas?**

1. **EmailJS não carrega**: Verifique conexão com internet
2. **Erro de configuração**: Verifique Service ID e User ID
3. **Emails não chegam**: Verifique spam/lixo eletrônico
4. **Templates não funcionam**: Verifique IDs dos templates

---

**🎯 Sistema pronto para envio real de emails!**


