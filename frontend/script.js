let currentUser = null;
let currentToken = null; // CHAVE: Armazena o Token de Acesso (JWT)

// 📢 CONFIGURAÇÃO DE PRODUÇÃO (EASYPANEL)
// O Frontend (quem usa este script) estará em: faculdade.morenadoaco.com.br
// O Backend (quem recebe as chamadas) estará em: api.morenadoaco.com.br

const BASE_URL_API = 'https://api.morenadoaco.com.br'; // Endereço público do Backend

const API_BASE_URL = `${BASE_URL_API}/api/v1`; 
const JWT_TOKEN_URL = `${BASE_URL_API}/api/token/`; 

// Usuários pré-definidos (Usados APENAS para simular a ROLE no Frontend visualmente)
const users = {
    admin: { password: 'admin', role: 'admin' },
    funcionario: { password: 'func', role: 'funcionario' }
};

// --- Funções de Inicialização e Controle de Acesso ---

function initializeUsers() {
    const pessoas = JSON.parse(localStorage.getItem('pessoas')) || [];
    const defaultUsers = {
        admin: { password: 'admin', role: 'admin' },
        funcionario: { password: 'func', role: 'funcionario' }
    };
    const newUsers = pessoas.reduce((acc, p) => {
        acc[p.nome] = { password: p.senha, role: p.role || 'usuario' };
        return acc;
    }, {...defaultUsers});

    Object.keys(users).forEach(key => delete users[key]);
    Object.assign(users, newUsers);
}

function updateNav() {
    document.querySelectorAll('.nav-item a').forEach(item => item.classList.add('hidden'));

    if (currentUser) {
        const username = Object.keys(users).find(key => users[key] === currentUser); 
        
        document.querySelectorAll('.all-logged a').forEach(item => item.classList.remove('hidden'));
        document.querySelectorAll(`.${currentUser.role} a`).forEach(item => item.classList.remove('hidden'));
        document.getElementById('loggedUsername').textContent = username;
        document.getElementById('loggedUserRole').textContent = currentUser.role.toUpperCase();

        updateDashboardData();
    }
}

function showPage(page) {
    document.querySelectorAll('.card').forEach(card => card.classList.add('hidden'));
    document.getElementById(page).classList.remove('hidden');

    if (page === 'cadastro-pessoas') updateListaPessoas();
    if (page === 'cadastro-produtos') updateListaProdutos();
    if (page === 'cadastro-fornecedores') updateListaFornecedores();
    if (page === 'dashboard') updateDashboardData();
}

// 🔑 LÓGICA DE LOGIN INTEGRADA COM A API (JWT/Bearer) 🔑
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(JWT_TOKEN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            alert('Credenciais inválidas! Verifique usuário e senha.');
            return; 
        }

        const data = await response.json();
        
        currentToken = data.access; 

        initializeUsers(); 
        currentUser = users[username] || { role: 'usuario' }; 
        
        showPage('dashboard');
        updateNav();

    } catch (error) {
        console.error('Erro de conexão com a API:', error);
        alert('Erro ao conectar com o servidor. Verifique se o Backend está online em ' + BASE_URL_API);
    }
    
    this.reset();
});

function logout() {
    currentUser = null;
    currentToken = null; 
    showPage('login');
    updateNav();
}

// --- Funções de Dashboard ---
async function updateDashboardData() {
    if (!currentToken) return;

    try {
        const response = await fetch(`${API_BASE_URL}/produtos/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${currentToken}` 
            }
        });
        
        if (!response.ok) {
            throw new Error('Falha ao buscar dados do Dashboard: ' + response.statusText);
        }

        const produtos = await response.json();
        
        const prodCount = produtos.length;
        const stockTotal = produtos.reduce((sum, p) => sum + p.quantidade, 0);
        const lowStockCount = produtos.filter(p => p.quantidade < 10).length;

        document.getElementById('dashboardProdCount').textContent = prodCount;
        document.getElementById('dashboardStockTotal').textContent = stockTotal;
        document.getElementById('dashboardLowStock').textContent = lowStockCount;

    } catch (error) {
        console.error('Erro no Dashboard API:', error);
        document.getElementById('dashboardProdCount').textContent = 0;
        document.getElementById('dashboardStockTotal').textContent = 0;
        document.getElementById('dashboardLowStock').textContent = 0;
    }

    if (currentUser && currentUser.role !== 'admin') {
         document.querySelector('#cadastro-pessoas h4.text-primary').classList.add('hidden');
         document.querySelector('#listaPessoas').classList.add('hidden');
    } else if (currentUser && currentUser.role === 'admin') {
         document.querySelector('#cadastro-pessoas h4.text-primary').classList.remove('hidden');
         document.querySelector('#listaPessoas').classList.remove('hidden');
    }
}

// --- Funções de Promoção/Gerenciamento de Usuários ---

async function promoteUser(userId, userName, newRole) {
    if (currentUser.role !== 'admin') {
        alert('Apenas administradores podem gerenciar o acesso de usuários.');
        return;
    }

    let payload = {};
    if (newRole === 'admin') {
        payload = { is_superuser: true, is_staff: true };
    } else if (newRole === 'funcionario') {
        payload = { is_superuser: false, is_staff: true }; 
    } else { // 'usuario'
        payload = { is_superuser: false, is_staff: false };
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/`, {
            method: 'PATCH', 
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Falha ao promover ${userName}. Erro: ${JSON.stringify(error)}`);
            return;
        }

        alert(`Usuário ${userName} promovido para ${newRole.toUpperCase()}! Ele deve fazer login novamente.`);
        await updateListaPessoas(); 
        
    } catch (error) {
        console.error('Erro na API de Promoção:', error);
        alert('Erro de conexão ao tentar alterar a permissão.');
    }
}

// 1. Pessoas (Listagem) - INTEGRADA COM API (GET)
async function updateListaPessoas() {
    const listaPessoas = document.getElementById('listaPessoas');
    listaPessoas.innerHTML = ''; 
    
    if (!currentToken) { 
        listaPessoas.innerHTML = '<li class="list-group-item text-danger">Faça login para ver a lista de usuários.</li>';
        return; 
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });

        if (!response.ok) {
             listaPessoas.innerHTML = '<li class="list-group-item text-danger">Erro: Você não tem permissão para listar usuários.</li>';
             return;
        }

        const djangoUsers = await response.json();

        // 1. Adiciona usuários padrão (apenas visualização local)
        if (currentUser && currentUser.role === 'admin') {
            ['admin', 'funcionario'].forEach(userKey => {
                const user = users[userKey];
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center bg-light text-muted';
                li.innerHTML = `<div><strong>${userKey}</strong> (Função: <span class="badge bg-danger">${user.role.toUpperCase()}</span>) - *Usuário Padrão Local*</div>`;
                listaPessoas.appendChild(li);
            });
        }
        
        // 2. Adiciona usuários da API
        djangoUsers.forEach(p => {
            const userId = p.id; 
            const currentRole = p.is_superuser ? 'admin' : (p.is_staff ? 'funcionario' : 'usuario'); 
            let promoteButtons = '';
            
            if (currentUser && currentUser.role === 'admin') {
                if (currentRole !== 'admin') {
                    promoteButtons += `<button class="btn btn-sm btn-danger ms-2" onclick="promoteUser(${userId}, '${p.username}', 'admin')">Tornar Admin</button>`;
                }
                if (currentRole !== 'funcionario' && currentRole !== 'admin') {
                    promoteButtons += `<button class="btn btn-sm btn-info ms-2" onclick="promoteUser(${userId}, '${p.username}', 'funcionario')">Tornar Funcionário</button>`;
                }
                if (currentRole !== 'usuario') {
                    promoteButtons += `<button class="btn btn-sm btn-secondary ms-2" onclick="promoteUser(${userId}, '${p.username}', 'usuario')">Rebaixar p/ Usuário</button>`;
                }
            }

            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.innerHTML = `<div>
                <strong>${p.username}</strong> (Função: <span class="badge ${currentRole === 'usuario' ? 'bg-secondary' : 'bg-success'}">${currentRole.toUpperCase()}</span>)
                </div>
                <div>
                ${promoteButtons}
                </div>`;
            listaPessoas.appendChild(li);
        });

    } catch (error) {
        console.error('Erro na API de Listagem de Usuários:', error);
        listaPessoas.innerHTML = `<li class="list-group-item text-danger">Erro ao carregar usuários.</li>`;
    }
}

// 📦 LÓGICA DE CADASTRO DE PESSOAS INTEGRADA COM API (POST) 📦
document.getElementById('cadastroForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const nome = document.getElementById('nome').value.trim();
    const idade = parseInt(document.getElementById('idade').value);
    const senha = document.getElementById('senha').value;
    
    const novoUsuario = { 
        username: nome, 
        password: senha,
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify(novoUsuario)
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Falha ao cadastrar. Erro: ${JSON.stringify(error)}`);
            return;
        }
        
        alert(`Usuário "${nome}" cadastrado no Django (MySQL) com sucesso! Agora pode fazer login.`);
        this.reset();
        showPage('login'); 
        
    } catch (error) {
        console.error('Erro na API de Cadastro de Usuário:', error);
        alert('Erro de conexão ao tentar cadastrar o usuário.');
    }
});

// 2. Fornecedores
async function updateListaFornecedores() {
    if (!currentToken) { return; }

    try {
        const response = await fetch(`${API_BASE_URL}/fornecedores/`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });

        if (!response.ok) {
             throw new Error('Falha ao buscar fornecedores: ' + response.statusText);
        }

        const fornecedores = await response.json();
        const listaFornecedores = document.getElementById('listaFornecedores');
        listaFornecedores.innerHTML = fornecedores.map(f => 
            `<li class="list-group-item">
                <div>
                    <strong>${f.nome}</strong> | CNPJ: ${f.cnpj}
                </div>
                <small class="text-muted">Email: ${f.email || 'N/A'} | Telefone: ${f.telefone || 'N/A'}</small>
            </li>`
        ).join('');
        
    } catch (error) {
        console.error('Erro na API de Fornecedores:', error);
        document.getElementById('listaFornecedores').innerHTML = `<li class="list-group-item text-danger">Não foi possível carregar os dados.</li>`;
    }
}

document.getElementById('fornecedorForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!currentToken) { alert('Erro: Não autenticado.'); return; }

    const novoFornecedor = {
        nome: document.getElementById('nomeFornecedor').value,
        cnpj: document.getElementById('cnpjFornecedor').value,
        telefone: document.getElementById('telefoneFornecedor').value,
        email: document.getElementById('emailFornecedor').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/fornecedores/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify(novoFornecedor)
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Falha ao cadastrar Fornecedor. Verifique os dados. Erro: ${JSON.stringify(error)}`);
            return;
        }

        alert(`Fornecedor cadastrado com sucesso na API!`);
        this.reset();
        await updateListaFornecedores(); 
        
    } catch (error) {
        console.error('Erro na API de Cadastro de Fornecedor:', error);
        alert('Erro de conexão ao tentar cadastrar.');
    }
});


// 3. Produtos
async function updateListaProdutos() {
    if (!currentToken) {
        document.getElementById('listaProdutos').innerHTML = '<li class="list-group-item text-danger">Erro: Não autenticado. Faça login novamente.</li>';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/produtos/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });

        if (!response.ok) {
             throw new Error('Falha ao buscar produtos: ' + response.statusText);
        }

        const produtos = await response.json();
        const listaProdutos = document.getElementById('listaProdutos');
        listaProdutos.innerHTML = ''; 
        
        listaProdutos.innerHTML = produtos.map(p => 
            `<li class="list-group-item ${p.quantidade < 10 ? 'border-danger' : ''}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${p.nome}</strong> (${p.codigo}) 
                        <span class="badge bg-secondary ms-2">${p.categoria}</span>
                    </div>
                    <div>
                        Qtd: <strong class="${p.quantidade < 10 ? 'text-danger' : 'text-success'}">${p.quantidade}</strong> 
                        | Preço: R$ ${parseFloat(p.preco).toFixed(2)}
                        ${p.quantidade < 10 ? '<span class="badge bg-danger ms-2">BAIXO ESTOQUE</span>' : ''}
                    </div>
                </div>
            </li>`
        ).join('');
        
        updateDashboardData();
    } catch (error) {
        console.error('Erro na API:', error);
        document.getElementById('listaProdutos').innerHTML = `<li class="list-group-item text-danger">Não foi possível carregar os dados: ${error.message}.</li>`;
    }
}

document.getElementById('produtoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!currentToken) { alert('Erro: Não autenticado.'); return; }

    const nome = document.getElementById('nomeProd').value;
    const codigo = document.getElementById('codigoProd').value.trim();
    const categoria = document.getElementById('categoria').value;
    const quantidade = parseInt(document.getElementById('quantidade').value);
    const preco = parseFloat(document.getElementById('preco').value);

    const novoProduto = { nome, codigo, categoria, quantidade, preco };

    try {
        const response = await fetch(`${API_BASE_URL}/produtos/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify(novoProduto)
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Falha ao cadastrar. Verifique o código/campos. Erro: ${JSON.stringify(error)}`);
            return;
        }

        alert(`Produto "${nome}" cadastrado com sucesso na API!`);
        this.reset();
        await updateListaProdutos(); 
        
    } catch (error) {
        console.error('Erro na API de Cadastro:', error);
        alert('Erro de conexão ao tentar cadastrar o produto.');
    }
});

// 4. Movimentações
function registrarMovimentacao(codigo, tipo, quantidade) {
    // MANTIDO POR COMPATIBILIDADE, NÃO USADO
    let movimentacoes = JSON.parse(localStorage.getItem('movimentacoes')) || [];
    movimentacoes.push({ 
        codigo, 
        tipo, 
        quantidade, 
        data: new Date().toLocaleString(),
        usuario: Object.keys(users).find(key => users[key] === currentUser) || 'Desconhecido'
    });
    localStorage.setItem('movimentacoes', JSON.stringify(movimentacoes));
}

document.getElementById('entradaForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!currentToken) { alert('Erro: Não autenticado.'); return; }
    
    const codigo = document.getElementById('codigoEntrada').value;
    const quantidade = parseInt(document.getElementById('quantidadeEntrada').value);
    
    const url_entrada = `${API_BASE_URL}/produtos/${codigo}/dar-entrada/`; 

    try {
        const response = await fetch(url_entrada, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify({ quantidade: quantidade })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Falha na Entrada. Erro: ${JSON.stringify(error)}`);
            return;
        }

        alert(`Entrada de ${quantidade} unidades do produto ${codigo} registrada na API!`);
        this.reset();
        await updateListaProdutos();
        
    } catch (error) {
        console.error('Erro na API de Entrada:', error);
        alert('Erro de conexão ao tentar registrar a entrada.');
    }
});

document.getElementById('saidaForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!currentToken) { alert('Erro: Não autenticado.'); return; }
    
    const codigo = document.getElementById('codigoSaida').value;
    const quantidade = parseInt(document.getElementById('quantidadeSaida').value);
    
    const url_saida = `${API_BASE_URL}/produtos/${codigo}/dar-saida/`;

    try {
        const response = await fetch(url_saida, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}` 
            },
            body: JSON.stringify({ quantidade: quantidade })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Falha na Saída. Verifique se há estoque. Erro: ${JSON.stringify(error)}`);
            return;
        }

        alert(`Saída de ${quantidade} unidades do produto ${codigo} registrada na API!`);
        this.reset();
        await updateListaProdutos(); 
        
    } catch (error) {
        console.error('Erro na API de Saída:', error);
        alert('Erro de conexão ao tentar registrar a saída.');
    }
});


// --- Consulta e Relatórios ---

document.getElementById('consultaForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!currentToken) { alert('Erro: Não autenticado.'); return; }
    
    const tipo = document.getElementById('tipoConsulta').value;
    const valor = document.getElementById('valorConsulta').value.trim();
    let url_consulta = `${API_BASE_URL}/produtos/`;

    if (tipo === 'codigo' && valor) {
        url_consulta = `${API_BASE_URL}/produtos/?codigo=${valor}`; 
    } else if (tipo === 'categoria' && valor) {
        url_consulta = `${API_BASE_URL}/produtos/?categoria=${valor}`; 
    } else if (tipo === 'todos') {
    } else {
        alert('Selecione um tipo de consulta ou forneça um valor válido.');
        return;
    }

    try {
        const response = await fetch(url_consulta, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${currentToken}` 
            }
        });

        if (!response.ok) {
            throw new Error('Falha na consulta: ' + response.statusText);
        }

        const resultados = await response.json();
        const htmlResultado = resultados.length > 0
            ? resultados.map(p => 
                `**${p.nome}** (${p.codigo}) | Categoria: ${p.categoria} | Qtd: **${p.quantidade}** | Preço: R$ ${parseFloat(p.preco).toFixed(2)}`
            ).join('<br>')
            : '<span class="text-muted">Nenhum resultado encontrado.</span>';

        document.getElementById('resultadoConsulta').innerHTML = htmlResultado;

    } catch (error) {
        console.error('Erro na API de Consulta:', error);
        document.getElementById('resultadoConsulta').innerHTML = `<span class="text-danger">Erro ao consultar: ${error.message}</span>`;
    }
});

document.getElementById('relatorioForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!currentToken) { alert('Erro: Não autenticado.'); return; }
    
    const tipo = document.getElementById('tipoRelatorio').value;
    let url_relatorio = `${API_BASE_URL}/movimentacoes-estoque/`;
    let relatorio_display = [];

    try {
        const response_mov = await fetch(url_relatorio, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });

        if (!response_mov.ok) {
            throw new Error('Falha ao buscar movimentações: ' + response_mov.statusText);
        }

        const movimentacoes = await response_mov.json();

        if (tipo === 'movimentacoes') {
            relatorio_display = movimentacoes
                .slice(-10) 
                .reverse() 
                .map(m => {
                    const style = m.tipo === 'E' ? 'text-success' : 'text-danger'; 
                    const icon = m.tipo === 'E' ? '⬆️' : '⬇️';
                    return `[${m.data_movimentacao}] | Tipo: <strong class="${style}">${icon} ${m.tipo === 'E' ? 'ENTRADA' : 'SAÍDA'}</strong> | Produto ID: ${m.id_produto} | Qtd: ${m.quantidade}`;
                });

        } else if (tipo === 'baixo') {
            const response_prod = await fetch(`${API_BASE_URL}/produtos/`, {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${currentToken}` }
            });
            const produtos = await response_prod.json();
            
            relatorio_display = produtos
                .filter(p => p.quantidade_atual < 10) 
                .map(p => `<span class="text-danger">⚠️ **${p.nome}** (${p.codigo || 'N/A'}) - Qtd: **${p.quantidade_atual}** (Necessita de reposição!)</span>`);
        }
        
        const htmlRelatorio = relatorio_display.length > 0
            ? relatorio_display.join('<br>')
            : '<span class="text-muted">Nenhum dado encontrado para este relatório.</span>';

        document.getElementById('resultadoRelatorio').innerHTML = htmlRelatorio;

    } catch (error) {
        console.error('Erro na API de Relatórios:', error);
        document.getElementById('resultadoRelatorio').innerHTML = `<span class="text-danger">Erro ao gerar relatório: ${error.message}</span>`;
    }
});


// --- Inicialização da Aplicação ---
initializeUsers(); 
showPage('login'); 
updateNav();