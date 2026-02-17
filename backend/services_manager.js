/**
 * Gerenciador de Serviços - EasyCut
 * Lógica para adicionar e listar serviços da barbearia
 */

const API_URL = 'http://localhost:5001';

// Função para carregar serviços ao iniciar a página
async function carregarServicos() {
    const user = JSON.parse(localStorage.getItem('currentUser'));
    
    if (!user || user.tipo !== 'barbearia') {
        console.error('Usuário não é uma barbearia ou não está logado');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/barbearias/${user.id}/services`);
        const data = await response.json();

        if (data.success) {
            renderizarListaServicos(data.services);
        } else {
            alert('Erro ao carregar serviços: ' + data.message);
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
}

// Função para renderizar a lista no HTML
function renderizarListaServicos(servicos) {
    const container = document.getElementById('lista-servicos'); // Seu elemento HTML onde a lista aparece
    if (!container) return;

    container.innerHTML = '';

    if (servicos.length === 0) {
        container.innerHTML = '<p>Nenhum serviço cadastrado.</p>';
        return;
    }

    servicos.forEach(servico => {
        const item = document.createElement('div');
        item.className = 'servico-item'; // Use suas classes CSS
        item.innerHTML = `
            <h4>${servico.nome_servico}</h4>
            <p>R$ ${parseFloat(servico.preco).toFixed(2)} - ${servico.duracao_minutos} min</p>
        `;
        container.appendChild(item);
    });
}

// Função para salvar novo serviço (chamar no submit do formulário)
async function salvarServico(event) {
    event.preventDefault();
    
    const user = JSON.parse(localStorage.getItem('currentUser'));
    
    // Pegar dados do formulário
    const nome = document.getElementById('nomeServico').value;
    const preco = document.getElementById('precoServico').value;
    const duracao = document.getElementById('duracaoServico').value;
    const descricao = document.getElementById('descricaoServico').value;

    const dadosServico = {
        barbearia_id: user.id,
        nome_servico: nome,
        preco: parseFloat(preco),
        duracao_minutos: parseInt(duracao),
        descricao: descricao
    };

    try {
        const response = await fetch(`${API_URL}/api/services/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dadosServico)
        });

        const result = await response.json();

        if (result.success) {
            alert('Serviço cadastrado com sucesso!');
            carregarServicos(); // Recarrega a lista
            document.getElementById('form-adicionar-servico').reset(); // Limpa o form
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        alert('Erro ao conectar com o servidor.');
    }
}
