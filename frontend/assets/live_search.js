/**
 * EasyCut - Busca em Tempo Real
 * Atualiza a lista de barbearias enquanto o usuário digita
 */

const API_BASE_URL = 'http://localhost:5001';

document.addEventListener('DOMContentLoaded', () => {
    // Tenta encontrar o campo de busca e o container de resultados
    // Ajuste os IDs conforme o seu HTML (ex: VisualizarBarbearias.html)
    const searchInput = document.getElementById('searchInput') || document.querySelector('input[type="search"]');
    const resultsContainer = document.getElementById('barbearias-list') || document.querySelector('.barbearias-container');
    const searchTypeRadios = document.querySelectorAll('input[name="searchType"]');
    
    let currentSearchType = 'name'; // Padrão

    // Listener para mudança de tipo de busca
    searchTypeRadios.forEach(radio => {
        if (radio.checked) currentSearchType = radio.value;
        
        radio.addEventListener('change', (e) => {
            currentSearchType = e.target.value;
            // Atualiza placeholder para guiar o usuário
            searchInput.placeholder = currentSearchType === 'name' 
                ? "Digite o nome da barbearia..." 
                : "Digite o bairro ou cidade...";
            
            // Opcional: Limpar busca ou refazer busca atual com novo filtro
            if (searchInput.value.trim()) performLiveSearch(searchInput.value.trim());
        });
    });

    if (!searchInput) {
        console.log('Campo de busca não encontrado nesta página.');
        return;
    }

    let debounceTimeout;

    // Evento disparado a cada tecla digitada
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.trim();
        
        // Limpa o timer anterior (evita chamadas excessivas)
        clearTimeout(debounceTimeout);

        // Aguarda 300ms após o usuário parar de digitar para buscar
        debounceTimeout = setTimeout(() => {
            performLiveSearch(term);
        }, 300);
    });

    async function performLiveSearch(term) {
        try {
            const payload = {
                name: term,
                search_type: currentSearchType
            };

            // Se tiver localização salva, envia junto para calcular distância
            // const userLoc = JSON.parse(localStorage.getItem('userLocation'));
            // if (userLoc) { payload.latitude = userLoc.lat; payload.longitude = userLoc.lng; }

            const response = await fetch(`${API_BASE_URL}/api/barbearias/nearby`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                renderLiveResults(data.barbearias);
            }
        } catch (error) {
            console.error('Erro na busca em tempo real:', error);
        }
    }

    function renderLiveResults(barbearias) {
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';

        if (barbearias.length === 0) {
            resultsContainer.innerHTML = '<div class="no-results" style="text-align:center; padding:20px;">Nenhuma barbearia encontrada com esse nome.</div>';
            return;
        }

        barbearias.forEach(barbearia => {
            // Cria o card da barbearia (ajuste o HTML conforme seu design)
            const card = document.createElement('div');
            card.className = 'barbearia-card';
            card.innerHTML = `
                <div class="card-content" style="border:1px solid #ddd; padding:15px; margin-bottom:10px; border-radius:8px; background:white;">
                    <h3 style="margin:0 0 5px 0;">${barbearia.name}</h3>
                    <p style="margin:0; color:#666;">${barbearia.address}</p>
                    ${barbearia.distance ? `<small>📍 ${barbearia.distance.toFixed(1)} km</small>` : ''}
                    <div style="margin-top:10px;"><a href="Agendamento.html?id=${barbearia.id}" style="color:#007bff; text-decoration:none; font-weight:bold;">Ver Detalhes</a></div>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }
});