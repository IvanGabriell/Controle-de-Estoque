// 📢 CONFIGURAÇÃO INTELIGENTE - Detecção automática de ambiente
let isLocalhost = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.');

// URLs base para diferentes ambientes
const ENV_CONFIG = {
    local: {
        API_BASE: 'http://localhost:8000',
        FRONTEND_BASE: 'http://localhost'
    },
    production: {
        API_BASE: 'https://api.morenadoaco.com.br',
        FRONTEND_BASE: 'https://faculdade.morenadoaco.com.br'
    }
};

// Seleciona configuração baseada no ambiente
const CONFIG = isLocalhost ? ENV_CONFIG.local : ENV_CONFIG.production;

// ✅ CONSTANTES
const BASE_URL_API = CONFIG.API_BASE;
const JWT_TOKEN_URL = `${BASE_URL_API}/api/token/`;
const API_BASE_URL = `${BASE_URL_API}/api`;
const FRONTEND_BASE = CONFIG.FRONTEND_BASE;

// ✅ LISTA INFALÍVEL DE ADMINS (SEMPRE serão admin, independente da API)
const ADMIN_USERS = [
    'admin',
    'administrador',
    'alexandre',      // ✅ VOCÊ É ADMIN
    'alex',           // ✅ Também admin
    'supervisor',
    'gerente',
    'diretor',
    'chefe',
    'master',
    'root'
];

// Log para debug
console.log('🌍 Ambiente:', isLocalhost ? 'Local' : 'Produção');
console.log('🔗 API URL:', BASE_URL_API);
console.log('🔐 Token URL:', JWT_TOKEN_URL);
console.log('📡 API Base URL:', API_BASE_URL);
console.log('🌐 Frontend URL:', FRONTEND_BASE);
console.log('👑 Admin users:', ADMIN_USERS);

// 📢 LÊ O ESTADO DO NAVEGADOR (sessionStorage)
let currentToken = sessionStorage.getItem('authToken') || null; 
let currentUser = JSON.parse(sessionStorage.getItem('userRole')) || null; 

// ==============================================================================
// FUNÇÕES AUXILIARES
// ==============================================================================

// ✅ FUNÇÃO INFALÍVEL PARA DETERMINAR ROLE
function getUserRole(username, apiUserData = {}) {
    const usernameLower = username.toLowerCase();
    
    console.log(`\n🔍 Determinando role para: ${username}`);
    
    // 1. PRIMEIRO: Verifica lista fixa de ADMINS
    const isInAdminList = ADMIN_USERS.some(adminUser => 
        usernameLower === adminUser.toLowerCase() || 
        usernameLower.includes(adminUser.toLowerCase())
    );
    
    if (isInAdminList) {
        console.log(`🎯 ADMIN DETECTADO: "${username}" está na lista de ADMINS`);
        return 'admin';
    }
    
    // 2. Verifica dados da API
    if (apiUserData.is_superuser === true || apiUserData.is_superuser === 1) {
        console.log(`🎯 ADMIN pela API: is_superuser = true`);
        return 'admin';
    }
    
    if (apiUserData.is_staff === true || apiUserData.is_staff === 1) {
        console.log(`👔 Funcionário pela API: is_staff = true`);
        return 'funcionario';
    }
    
    // 3. Heurística por palavras-chave no username
    const adminKeywords = ['admin', 'adm', 'gerente', 'supervisor', 'diretor', 'chefe', 'master', 'root'];
    const hasAdminKeyword = adminKeywords.some(keyword => usernameLower.includes(keyword));
    
    if (hasAdminKeyword) {
        console.log(`🎯 ADMIN por palavra-chave: "${username}" contém termo administrativo`);
        return 'admin';
    }
    
    // 4. Default
    console.log(`👤 Usuário padrão: "${username}"`);
    return 'usuario';
}

function checkAuthState() {
    const isLoginPage = window.location.pathname.includes('index.html') || 
                       window.location.pathname === '/';
    
    if (!isLoginPage && !currentToken) {
        showMessage('Sessão expirada. Faça login novamente.', 'warning');
        setTimeout(() => {
            window.location.href = `${FRONTEND_BASE}/index.html`;
        }, 2000);
    }
}

function updateNav() {
    document.querySelectorAll('.nav-item a').forEach(item => item.classList.add('hidden'));

    if (currentUser) {
        const username = sessionStorage.getItem('username') || 'Usuário';
        
        document.querySelectorAll('.nav-item a').forEach(item => item.classList.remove('hidden'));
        document.querySelectorAll(`.${currentUser.role} a`).forEach(item => item.classList.remove('hidden'));
        
        if (document.getElementById('loggedUsername')) {
            document.getElementById('loggedUsername').textContent = username;
            document.getElementById('loggedUserRole').textContent = currentUser.role.toUpperCase();
        }
    }
}

function showMessage(text, type = 'info') {
    const messageDiv = document.getElementById('loginMessage');
    if (messageDiv) {
        let icon, bgColor, borderColor, textColor;
        
        switch(type) {
            case 'success':
                icon = 'check-circle';
                bgColor = 'rgba(6, 214, 160, 0.1)';
                borderColor = '#06d6a0';
                textColor = '#06a67e';
                break;
            case 'warning':
                icon = 'exclamation-triangle';
                bgColor = 'rgba(255, 209, 102, 0.1)';
                borderColor = '#ffd166';
                textColor = '#d4a430';
                break;
            case 'danger':
                icon = 'times-circle';
                bgColor = 'rgba(239, 71, 111, 0.1)';
                borderColor = '#ef476f';
                textColor = '#d4335c';
                break;
            default:
                icon = 'info-circle';
                bgColor = 'rgba(67, 97, 238, 0.1)';
                borderColor = '#4361ee';
                textColor = '#4361ee';
        }
        
        messageDiv.innerHTML = `
            <div style="background: ${bgColor}; color: ${textColor}; padding: 15px 20px; border-radius: 12px; border-left: 4px solid ${borderColor}; display: flex; align-items: center; gap: 12px;">
                <i class="bi bi-${icon}" style="font-size: 1.2rem;"></i>
                <div>${text}</div>
            </div>
        `;
        messageDiv.classList.remove('d-none');
        
        if (type !== 'success') {
            setTimeout(() => {
                if (messageDiv) {
                    messageDiv.classList.add('d-none');
                }
            }, 5000);
        }
    }
}

function animateLoginButton(isLoading) {
    const submitBtn = document.getElementById('submitBtn');
    if (!submitBtn) return;
    
    if (isLoading) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <span>Autenticando...</span>
        `;
        submitBtn.style.opacity = '0.8';
    } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <span>Entrar no Sistema</span>
            <i class="bi bi-arrow-right"></i>
        `;
        submitBtn.style.opacity = '1';
    }
}

// ✅ FUNÇÃO ATUALIZADA: Usa a lista de admins
async function getCurrentUser(token, username) {
    try {
        console.log(`\n🔍 Iniciando busca para: ${username}`);
        
        let apiUserData = {};
        
        // Tenta buscar da API
        try {
            const response = await fetch(`${API_BASE_URL}/users/`, {
                method: 'GET',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                timeout: 5000
            });
            
            if (response.ok) {
                const userData = await response.json();
                const usersArray = userData.results || userData || [];
                
                apiUserData = usersArray.find(user => 
                    user.username && user.username.toLowerCase() === username.toLowerCase()
                ) || {};
                
                console.log('📊 Dados da API:', apiUserData);
            } else {
                console.warn(`⚠️ API users retornou ${response.status}`);
            }
        } catch (apiError) {
            console.warn('⚠️ Erro na API, usando fallback:', apiError.message);
        }
        
        // ✅ DETERMINA ROLE USANDO FUNÇÃO INFALÍVEL
        const userRole = getUserRole(username, apiUserData);
        
        console.log(`\n✅ RESULTADO FINAL:`);
        console.log(`👤 Usuário: ${username}`);
        console.log(`🎭 Role: ${userRole.toUpperCase()}`);
        console.log(`👑 É admin? ${userRole === 'admin' ? 'SIM ✅' : 'NÃO ❌'}`);
        
        // Cria objeto de usuário
        const userObj = {
            id: apiUserData.id || 1,
            username: username,
            email: apiUserData.email || `${username}@empresa.com`,
            is_superuser: userRole === 'admin',
            is_staff: userRole === 'admin' || userRole === 'funcionario',
            role: userRole
        };
        
        console.log('📋 Objeto do usuário:', userObj);
        
        return userObj;
        
    } catch (error) {
        console.error('❌ Erro crítico:', error);
        
        // Fallback extremamente seguro
        const userRole = getUserRole(username, {});
        
        return {
            id: 1,
            username: username,
            email: `${username}@empresa.com`,
            is_superuser: userRole === 'admin',
            is_staff: userRole === 'admin',
            role: userRole
        };
    }
}

// ==============================================================================
// LÓGICA DE LOGIN
// ==============================================================================

document.getElementById('loginForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showMessage('Por favor, preencha todos os campos.', 'warning');
        return;
    }
    
    animateLoginButton(true);
    
    try {
        console.log(`\n🚀 INICIANDO LOGIN PARA: ${username}`);
        
        const tokenResponse = await fetch(JWT_TOKEN_URL, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json', 
                'Accept': 'application/json' 
            },
            body: JSON.stringify({ 
                username: username, 
                password: password 
            })
        });

        if (!tokenResponse.ok) {
            const errorData = await tokenResponse.json().catch(() => ({}));
            const message = tokenResponse.status === 401 
                ? 'Credenciais inválidas! Verifique usuário e senha.' 
                : `Erro ${tokenResponse.status}: ${errorData.detail || 'Falha na autenticação'}`;
            showMessage(message, 'danger');
            animateLoginButton(false);
            return; 
        }

        const tokenData = await tokenResponse.json();
        const token = tokenData.access; 
        
        console.log('✅ Token JWT obtido com sucesso');
        sessionStorage.setItem('authToken', token);
        
        // Obtém dados do usuário
        const userData = await getCurrentUser(token, username);
        
        console.log(`\n🎉 LOGIN BEM-SUCEDIDO!`);
        console.log(`👤 Nome: ${userData.username}`);
        console.log(`🎭 Role: ${userData.role.toUpperCase()}`);
        console.log(`👑 Admin: ${userData.role === 'admin' ? 'SIM' : 'NÃO'}`);
        
        // Salva todos os dados
        sessionStorage.setItem('userRole', JSON.stringify({
            role: userData.role,
            username: userData.username,
            email: userData.email,
            id: userData.id,
            is_admin: userData.role === 'admin',
            is_superuser: userData.is_superuser
        }));
        
        sessionStorage.setItem('username', userData.username);
        sessionStorage.setItem('user_id', userData.id);
        sessionStorage.setItem('is_admin', userData.role === 'admin');
        sessionStorage.setItem('user_role', userData.role);
        
        // Atualiza variáveis globais
        currentToken = token;
        currentUser = {
            role: userData.role,
            username: userData.username,
            is_admin: userData.role === 'admin'
        };
        
        // Mensagem personalizada por role
        let welcomeMessage = `Bem-vindo, ${userData.username}!`;
        if (userData.role === 'admin') {
            welcomeMessage = `👑 Administrador ${userData.username}, acesso total liberado!`;
        } else if (userData.role === 'funcionario') {
            welcomeMessage = `👔 Funcionário ${userData.username}, bem-vindo ao sistema!`;
        }
        
        showMessage(`${welcomeMessage} Redirecionando...`, 'success');
        
        // Animação especial para admin
        setTimeout(() => {
            const submitBtn = document.getElementById('submitBtn');
            if (submitBtn) {
                if (userData.role === 'admin') {
                    submitBtn.innerHTML = `
                        <i class="bi bi-shield-check me-2"></i>
                        <span>ACESSO ADMIN CONCEDIDO</span>
                    `;
                    submitBtn.style.background = 'linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%)';
                    submitBtn.style.boxShadow = '0 5px 15px rgba(67, 97, 238, 0.4)';
                } else {
                    submitBtn.innerHTML = `
                        <i class="bi bi-check-circle me-2"></i>
                        <span>Login realizado com sucesso!</span>
                    `;
                    submitBtn.style.background = 'linear-gradient(135deg, #06d6a0 0%, #06a67e 100%)';
                }
            }
        }, 500);
        
        // Redireciona
        setTimeout(() => {
            window.location.href = `${FRONTEND_BASE}/dashboard.html`;
        }, 1500);
        
    } catch (error) {
        console.error('❌ Erro de conexão com a API:', error);
        showMessage('Erro de conexão com o servidor. Verifique se a API está rodando.', 'danger');
        animateLoginButton(false);
    }
});

function logout() {
    showMessage('Saindo do sistema...', 'info');
    
    setTimeout(() => {
        sessionStorage.clear();
        currentToken = null;
        currentUser = null;
        window.location.href = `${FRONTEND_BASE}/index.html`;
    }, 1000);
}

// ==============================================================================
// INICIALIZAÇÃO
// ==============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('\n🚀 SISTEMA INICIALIZADO');
    console.log('🔑 Token presente:', !!currentToken);
    console.log('👤 Usuário atual:', currentUser);
    console.log('👑 É admin?', currentUser?.role === 'admin' ? 'SIM ✅' : 'NÃO ❌');
    console.log('👥 Lista de ADMINS:', ADMIN_USERS);
    
    const isLoginPage = window.location.pathname.includes('index.html') || 
                       window.location.pathname === '/';
    
    if (isLoginPage && currentToken) {
        const messageDiv = document.getElementById('loginMessage');
        if (messageDiv) {
            const roleText = currentUser?.role === 'admin' ? '👑 ADMINISTRADOR' :
                           currentUser?.role === 'funcionario' ? '👔 FUNCIONÁRIO' : '👤 USUÁRIO';
            
            messageDiv.innerHTML = `
                <div style="background: rgba(67, 97, 238, 0.1); color: #4361ee; padding: 15px; border-radius: 12px; border-left: 4px solid #4361ee;">
                    <i class="bi bi-shield-check me-2"></i>
                    <strong>Você já está logado!</strong>
                    <div class="mt-1">
                        Usuário: <strong>${currentUser?.username || 'usuário'}</strong><br>
                        Nível: <strong>${roleText}</strong>
                    </div>
                    <div class="mt-2">
                        <a href="dashboard.html" class="btn btn-sm btn-primary me-2">
                            <i class="bi bi-speedometer2 me-1"></i>Ir para o Dashboard
                        </a>
                        <button onclick="logout()" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-box-arrow-right me-1"></i>Sair
                        </button>
                    </div>
                </div>
            `;
            messageDiv.classList.remove('d-none');
        }
    }
    
    checkAuthState();
    updateNav();
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
});