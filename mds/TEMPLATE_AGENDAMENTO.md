# 📧 Template de Agendamento - EmailJS

## 🎯 **Configuração do Template de Agendamento**

### **1. Criar Template no EmailJS**

1. **Acesse**: https://www.emailjs.com/
2. **Vá em**: "Email Templates"
3. **Clique em**: "Create New Template"

### **2. Configurar Template**

#### **Configurações Básicas:**
- **Template ID**: `template_appointment`
- **Template Name**: `Confirmação de Agendamento EasyCut`
- **Subject**: `Agendamento Confirmado - {{barbearia_name}}`

#### **Conteúdo do Template:**
```html
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 20px;">
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="margin: 0; font-size: 2rem;">🎉 Agendamento Confirmado!</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem;">EasyCut - Sistema de Agendamento</p>
    </div>
    
    <!-- Content -->
    <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <h2 style="color: #333; margin-top: 0;">Olá, {{to_name}}!</h2>
        
        <p style="color: #666; font-size: 1rem; line-height: 1.6;">
            Seu agendamento foi confirmado com sucesso! Aqui estão os detalhes:
        </p>
        
        <!-- Detalhes do Agendamento -->
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
            <h3 style="color: #10b981; margin-top: 0;">📋 Detalhes do Agendamento</h3>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #333;">🏪 Barbearia:</strong>
                <span style="color: #666; margin-left: 10px;">{{barbearia_name}}</span>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #333;">📍 Endereço:</strong>
                <span style="color: #666; margin-left: 10px;">{{barbearia_address}}</span>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #333;">📅 Data:</strong>
                <span style="color: #666; margin-left: 10px;">{{appointment_date}}</span>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #333;">🕐 Horário:</strong>
                <span style="color: #666; margin-left: 10px;">{{appointment_time}}</span>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #333;">✂️ Serviços:</strong>
                <span style="color: #666; margin-left: 10px;">{{services}}</span>
            </div>
            
            <div style="margin-bottom: 0; padding-top: 15px; border-top: 1px solid #ddd;">
                <strong style="color: #333; font-size: 1.1rem;">💰 Valor Total:</strong>
                <span style="color: #10b981; font-size: 1.2rem; font-weight: bold; margin-left: 10px;">{{total_price}}</span>
            </div>
        </div>
        
        <!-- Instruções -->
        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
            <h3 style="color: #3b82f6; margin-top: 0;">📞 Próximos Passos</h3>
            <ul style="color: #666; margin: 0; padding-left: 20px;">
                <li>Chegue 10 minutos antes do horário agendado</li>
                <li>Traga um documento de identificação</li>
                <li>Em caso de cancelamento, entre em contato com a barbearia</li>
                <li>Você receberá um lembrete 1 hora antes do agendamento</li>
            </ul>
        </div>
        
        <!-- Botão de Contato -->
        <div style="text-align: center; margin: 30px 0;">
            <a href="mailto:{{barbearia_name}}@easycut.com" style="background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                📧 Entrar em Contato
            </a>
        </div>
        
        <p style="color: #666; font-size: 0.9rem; text-align: center; margin-top: 30px;">
            Obrigado por escolher o EasyCut! 🎯
        </p>
    </div>
    
    <!-- Footer -->
    <div style="text-align: center; margin-top: 20px; color: #999; font-size: 0.8rem;">
        <p>© 2024 EasyCut - Todos os direitos reservados</p>
        <p>Este é um email automático, não responda a esta mensagem.</p>
    </div>
</div>
```

### **3. Salvar Template**

1. **Clique em**: "Save"
2. **Verifique**: Se o Template ID está como `template_appointment`

## 🧪 **Como Testar**

### **1. Fazer Login**
- Acesse `Login.html`
- Faça login com um usuário cadastrado

### **2. Agendar Serviço**
- Vá para `BarbeariaDetalhes.html?id=1`
- Selecione serviços, data e horário
- Clique em "Confirmar Agendamento"

### **3. Verificar Email**
- Email de confirmação deve chegar
- Deve conter todos os detalhes do agendamento

## 🔧 **Variáveis do Template**

### **Variáveis Disponíveis:**
- `{{to_name}}` - Nome do cliente
- `{{to_email}}` - Email do cliente
- `{{barbearia_name}}` - Nome da barbearia
- `{{barbearia_address}}` - Endereço da barbearia
- `{{appointment_date}}` - Data do agendamento
- `{{appointment_time}}` - Horário do agendamento
- `{{services}}` - Serviços selecionados
- `{{total_price}}` - Valor total
- `{{from_name}}` - Nome do remetente (EasyCut)

## ✅ **Pronto!**

Após configurar o template, o sistema enviará automaticamente emails de confirmação de agendamento para todos os usuários que fizerem agendamentos!

---

**Sistema de agendamento com email implementado!** 📧✨
