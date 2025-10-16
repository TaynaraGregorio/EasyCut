/**
 * Sistema de Cadastro Simplificado - EasyCut
 * Versão sem confirmação de email para testes
 */

class SimpleAuthService {
    constructor() {
        // Inicializar dados de usuários no localStorage
        this.initUserData();
    }
    
    initUserData() {
        if (!localStorage.getItem('users')) {
            localStorage.setItem('users', JSON.stringify([]));
        }
    }
    
    /**
     * Cadastra usuário sem confirmação de email
     */
    async registerUser(userData) {
        try {
            // Verificar se email já existe
            const users = JSON.parse(localStorage.getItem('users'));
            const existingUser = users.find(u => u.email === userData.email);
            
            if (existingUser) {
                return {
                    success: false,
                    message: 'Este email já está cadastrado. Tente fazer login.'
                };
            }
            
            // Criar usuário com email já verificado
            const newUser = {
                ...userData,
                emailVerified: true, // Já verificado para testes
                createdAt: new Date().toISOString(),
                id: Date.now()
            };
            
            // Salvar usuário
            users.push(newUser);
            localStorage.setItem('users', JSON.stringify(users));
            
            console.log('✅ Usuário cadastrado com sucesso!');
            console.log('👤 Usuário:', newUser);
            
            return {
                success: true,
                message: 'Cadastro realizado com sucesso! Você já pode fazer login.',
                user: newUser
            };
            
        } catch (error) {
            console.error('Erro no cadastro:', error);
            return {
                success: false,
                message: 'Erro ao realizar cadastro. Tente novamente.'
            };
        }
    }
    
    /**
     * Autentica usuário (login)
     */
    authenticateUser(email, password) {
        try {
            const users = JSON.parse(localStorage.getItem('users'));
            const user = users.find(u => u.email === email);
            
            if (!user) {
                return {
                    success: false,
                    message: 'Email não encontrado. Verifique se está correto.'
                };
            }
            
            if (user.senha !== password) {
                return {
                    success: false,
                    message: 'Senha incorreta. Tente novamente.'
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
     * Lista todos os usuários cadastrados (para debug)
     */
    listUsers() {
        const users = JSON.parse(localStorage.getItem('users'));
        console.log('👥 Usuários cadastrados:', users);
        return users;
    }
    
    /**
     * Limpa todos os usuários (para reset)
     */
    clearUsers() {
        localStorage.setItem('users', JSON.stringify([]));
        console.log('🗑️ Todos os usuários foram removidos');
    }
}

// Instância global do serviço de autenticação simplificado
window.simpleAuth = new SimpleAuthService();

console.log('🔧 Sistema de autenticação simplificado carregado!');
console.log('💡 Para listar usuários: simpleAuth.listUsers()');
console.log('💡 Para limpar usuários: simpleAuth.clearUsers()');






