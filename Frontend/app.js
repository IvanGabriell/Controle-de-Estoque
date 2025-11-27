// 📢 LÊ O ESTADO DO NAVEGADOR (sessionStorage)
let currentToken = sessionStorage.getItem('authToken') || null; 
let currentUser = JSON.parse(sessionStorage.getItem('userRole')) || null; 

// CONFIGURAÇÃO DE PRODUÇÃO (EasyPanel)
const BASE_URL_API = 'https://api.morenadoaco.com.br'; 
const JWT_TOKEN_URL = `${BASE_URL_API}/api/token/`; 
const API_BASE_URL = `${BASE_URL_API}/api/v1`; 

// Usuários pré-definidos (Usados APENAS para simular a ROLE no Frontend visualmente)
const users = {
    admin: { password: 'admin', role: 'admin' },
    funcionario: { password: 'func', role: 'funcionario' }
};

// --- Funções de Inicialização e Controle de Acesso ---

function initializeUsers() {
    // Mantém a lógica de mapeamento de roles locais, se houver
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

/**
 * 🚨 FUNÇÃO CRÍTICA PARA MPA: Verifica se o usuário está autenticado
 */
function checkAuthState() {
    // Se a página não for o index.html (login)
    if (window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
        if (!currentToken) {
            alert('Sessão expirada. Faça login novamente.');
            window.location.href = '/index.html';
        }
    }
}

function updateNav() {
    // Atualiza a navegação e dashboard com a role do sessionStorage
    document.querySelectorAll('.nav-item a').forEach(item => item.classList.add('hidden'));

    if (currentUser) {
        const username = Object.keys(users).find(key => users[key] === currentUser); 
        
        document.querySelectorAll('.all-logged a').forEach(item => item.classList.remove('hidden'));
        document.querySelectorAll(`.${currentUser.role} a`).forEach(item => item.classList.remove('hidden'));
        
        // As páginas precisam ter esses elementos para exibir o nome e a role
        if (document.getElementById('loggedUsername')) {
             document.getElementById('loggedUsername').textContent = username;
             document.getElementById('loggedUserRole').textContent = currentUser.role.toUpperCase();
        }
    }
}

// Em MPA, showPage apenas redireciona (a lógica de esconder/mostrar DIVs não existe mais)
function showPage(page) {
    if (page === 'cadastro-pessoas') { window.location.href = '/cadastro-pessoas.html'; }
    else if (page === 'dashboard') { window.location.href = '/dashboard.html'; }
    // As outras páginas devem ser mapeadas aqui
}

// 🔑 LÓGICA DE LOGIN INTEGRADA COM A API (JWT/Bearer) 🔑
document.getElementById('loginForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(JWT_TOKEN_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            alert('Credenciais inválidas! Verifique usuário e senha.');
            return; 
        }

        const data = await response.json();
        const token = data.access; 
        sessionStorage.setItem('authToken', token); // 🚨 NOVO: SALVA O TOKEN

        // Segunda chamada para obter a role
        const userDetailsResponse = await fetch(`${API_BASE_URL}/users/?username=${username}`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const userData = await userDetailsResponse.json();
        
        if (userData.length > 0) {
            const user = userData[0]; 
            let userRole = user.is_superuser ? 'admin' : (user.is_staff ? 'funcionario' : 'usuario');
            const userRoleObject = { role: userRole };
            
            sessionStorage.setItem('userRole', JSON.stringify(userRoleObject)); // 🚨 NOVO: SALVA A ROLE

            window.location.href = '/dashboard.html'; // 🚨 REDIRECIONA PARA A NOVA PÁGINA
            
        } else {
            alert('Erro: Usuário não encontrado após login.');
        }

    } catch (error) {
        console.error('Erro de conexão com a API:', error);
        alert('Erro ao conectar com o servidor. Verifique o console para detalhes.');
    }
    
    this.reset();
});

function logout() {
    sessionStorage.removeItem('authToken'); // 🚨 LIMPA TUDO
    sessionStorage.removeItem('userRole'); 
    currentToken = null;
    currentUser = null;
    window.location.href = '/index.html'; // Redireciona para o login
}

// --- Funções de Dashboard (Invocadas na inicialização de cada página) ---
async function updateDashboardData() {
    if (!currentToken) return; // Proteção

    try {
        const response = await fetch(`${API_BASE_URL}/produtos/`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        // ... (resto da lógica de dashboard) ...
        const produtos = await response.json();
        const prodCount = produtos.length;
        const stockTotal = produtos.reduce((sum, p) => sum + p.quantidade, 0);
        const lowStockCount = produtos.filter(p => p.quantidade < 10).length;

        if (document.getElementById('dashboardProdCount')) {
             document.getElementById('dashboardProdCount').textContent = prodCount;
             document.getElementById('dashboardStockTotal').textContent = stockTotal;
             document.getElementById('dashboardLowStock').textContent = lowStockCount;
        }

    } catch (error) {
        console.error('Erro no Dashboard API:', error);
    }
}

// [Omitindo o resto das funções (updateListaPessoas, promoteUser, etc.) por brevidade. 
// O código deve assumir que você as manterá no app.js, e cada novo HTML chamará a função relevante.]


// ==============================================================================
// 🏁 INICIALIZAÇÃO DA APLICAÇÃO (Rodado em CADA página HTML)
// ==============================================================================
initializeUsers(); 
checkAuthState(); // 🚨 NOVO: Verifica se há token antes de rodar qualquer outra função
updateNav(); // Atualiza o NavBar em todas as páginas