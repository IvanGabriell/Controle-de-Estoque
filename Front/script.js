 let currentUser = null;

        // Usuários pré-definidos (Administração e Funcionários)
        const users = {
            admin: { password: 'admin', role: 'admin' },
            funcionario: { password: 'func', role: 'funcionario' }
            // Usuários com role 'usuario' (ou promovidos) são adicionados dinamicamente
        };

        // --- Funções de Inicialização e Controle de Acesso ---

        /**
         * Carrega os usuários salvos no localStorage para o objeto 'users'.
         */
        function initializeUsers() {
            const pessoas = JSON.parse(localStorage.getItem('pessoas')) || [];
            
            // Remove usuários dinâmicos antigos antes de adicionar os novos do localStorage
            Object.keys(users).forEach(key => {
                // Mantém admin e funcionario pre-definidos, remove o resto
                if (key !== 'admin' && key !== 'funcionario') {
                    delete users[key];
                }
            });

            pessoas.forEach(p => {
                // Adiciona ou atualiza o usuário com a role armazenada
                users[p.nome] = { password: p.senha, role: p.role || 'usuario' };
            });
        }

        /**
         * Atualiza a visibilidade dos itens de navegação com base na role do usuário logado.
         */
        function updateNav() {
            // Oculta todos os itens inicialmente
            document.querySelectorAll('.nav-item a').forEach(item => item.classList.add('hidden'));

            if (currentUser) {
                const username = Object.keys(users).find(key => users[key] === currentUser);
                // Exibe itens de navegação apropriados
                document.querySelectorAll('.all-logged a').forEach(item => item.classList.remove('hidden'));
                document.querySelectorAll(`.${currentUser.role} a`).forEach(item => item.classList.remove('hidden'));
                document.getElementById('loggedUsername').textContent = username;
                document.getElementById('loggedUserRole').textContent = currentUser.role.toUpperCase();

                // Atualiza o Dashboard com dados
                updateDashboardData();
            }
        }

        /**
         * Oculta todas as páginas e exibe apenas a página solicitada.
         */
        function showPage(page) {
            document.querySelectorAll('.card').forEach(card => card.classList.add('hidden'));
            document.getElementById(page).classList.remove('hidden');

            // Atualiza listas ao navegar (para garantir que os dados mais recentes sejam exibidos)
            if (page === 'cadastro-pessoas') updateListaPessoas();
            if (page === 'cadastro-produtos') updateListaProdutos();
            if (page === 'cadastro-fornecedores') updateListaFornecedores();
            if (page === 'dashboard') updateDashboardData();
        }

        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            initializeUsers(); // Recarrega os usuários cadastrados antes de tentar o login

            if (users[username] && users[username].password === password) {
                currentUser = users[username];
                showPage('dashboard');
                updateNav();
            } else {
                alert('Credenciais inválidas! Verifique usuário e senha.');
            }
            this.reset();
        });

        function logout() {
            currentUser = null;
            showPage('login');
            updateNav();
        }
        
        // --- Funções de Dashboard ---
        function updateDashboardData() {
            const produtos = JSON.parse(localStorage.getItem('produtos')) || [];
            
            const prodCount = produtos.length;
            const stockTotal = produtos.reduce((sum, p) => sum + p.quantidade, 0);
            const lowStockCount = produtos.filter(p => p.quantidade < 10).length;

            document.getElementById('dashboardProdCount').textContent = prodCount;
            document.getElementById('dashboardStockTotal').textContent = stockTotal;
            document.getElementById('dashboardLowStock').textContent = lowStockCount;

            // Se o usuário não for Admin, ocultar a seção de gerenciamento de pessoas no menu, mas manter a tela.
            if (currentUser && currentUser.role !== 'admin') {
                 // Ocultar a seção de gerenciamento de pessoas (se for o caso)
                 document.querySelector('#cadastro-pessoas h4.text-primary').classList.add('hidden');
                 document.querySelector('#listaPessoas').classList.add('hidden');
            } else if (currentUser && currentUser.role === 'admin') {
                // Garante que esteja visível se for admin
                 document.querySelector('#cadastro-pessoas h4.text-primary').classList.remove('hidden');
                 document.querySelector('#listaPessoas').classList.remove('hidden');
            }
        }

        // --- Funções de Promoção/Gerenciamento de Usuários ---

        /**
         * Promove ou muda a função de um usuário dinâmico.
         */
        function promoteUser(userName, newRole) {
            if (currentUser.role !== 'admin') {
                alert('Apenas administradores podem gerenciar o acesso de usuários.');
                return;
            }

            // Impede a alteração da role dos usuários padrões 'admin' e 'funcionario'
            if (userName === 'admin' || userName === 'funcionario') {
                alert('Não é possível alterar a função dos usuários padrão (admin, funcionario).');
                return;
            }

            let pessoas = JSON.parse(localStorage.getItem('pessoas')) || [];
            const pessoaIndex = pessoas.findIndex(p => p.nome === userName);

            if (pessoaIndex > -1) {
                pessoas[pessoaIndex].role = newRole;
                localStorage.setItem('pessoas', JSON.stringify(pessoas));
                
                // Atualiza o estado do aplicativo
                initializeUsers();
                updateListaPessoas();
                updateNav(); 
                
                alert(`Usuário "${userName}" promovido para a função: ${newRole.toUpperCase()}! Ele deverá fazer login novamente para que o novo acesso seja aplicado.`);
            } else {
                alert('Erro: Usuário não encontrado na lista de pessoas cadastradas.');
            }
        }


        // --- Funções de Listagem e Persistência (LocalStorage) ---

        // 1. Pessoas (Usuários Simples)
        function updateListaPessoas() {
            const pessoas = JSON.parse(localStorage.getItem('pessoas')) || [];
            const listaPessoas = document.getElementById('listaPessoas');
            listaPessoas.innerHTML = ''; // Limpa a lista antes de preencher

            // Adiciona usuários padrão ao topo da lista (apenas para visualização do admin)
            if (currentUser && currentUser.role === 'admin') {
                ['admin', 'funcionario'].forEach(userKey => {
                    const user = users[userKey];
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center bg-light text-muted';
                    li.innerHTML = `<div>
                        <strong>${userKey}</strong> (Função: <span class="badge bg-danger">${user.role.toUpperCase()}</span>) - *Usuário Padrão*
                        </div>
                        <div>
                        <button class="btn btn-sm btn-outline-danger ms-2" disabled>Acesso Fixo</button>
                        </div>`;
                    listaPessoas.appendChild(li);
                });
            }

            // Adiciona usuários dinâmicos (cadastrados)
            pessoas.forEach(p => {
                const currentRole = p.role || 'usuario';
                let promoteButtons = '';
                
                if (currentUser && currentUser.role === 'admin') {
                    // Botão para tornar os corno em ADMIN
                    if (currentRole !== 'admin') {
                        promoteButtons += `<button class="btn btn-sm btn-danger ms-2" onclick="promoteUser('${p.nome}', 'admin')">Tornar Admin</button>`;
                    }

                    // Botão para tornar os corno em FUNCIONARIO
                    if (currentRole !== 'funcionario' && currentRole !== 'admin') {
                        promoteButtons += `<button class="btn btn-sm btn-info ms-2" onclick="promoteUser('${p.nome}', 'funcionario')">Tornar Funcionário</button>`;
                    }

                    // Botão para tornar os corno em USUARIO (rebaixar)
                    if (currentRole !== 'usuario') {
                        promoteButtons += `<button class="btn btn-sm btn-secondary ms-2" onclick="promoteUser('${p.nome}', 'usuario')">Rebaixar p/ Usuário</button>`;
                    }
                }

                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `<div>
                    <strong>${p.nome}</strong> (Função: <span class="badge ${currentRole === 'usuario' ? 'bg-secondary' : 'bg-success'}">${currentRole.toUpperCase()}</span>) - Idade: ${p.idade}
                    </div>
                    <div>
                    ${promoteButtons}
                    </div>`;
                listaPessoas.appendChild(li);
            });

            // Se for funcionário ou usuário simples, remove os botões de promoção
            if (currentUser && currentUser.role !== 'admin') {
                listaPessoas.querySelectorAll('.btn').forEach(btn => btn.remove());
            }

            // Esconde a lista se não for admin
            if (currentUser && currentUser.role !== 'admin') {
                document.querySelector('#cadastro-pessoas h4').classList.add('hidden');
            } else if (document.querySelector('#cadastro-pessoas h4')) {
                 document.querySelector('#cadastro-pessoas h4').classList.remove('hidden');
            }
        }

        document.getElementById('cadastroForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const nome = document.getElementById('nome').value.trim();
            const idade = parseInt(document.getElementById('idade').value);
            const senha = document.getElementById('senha').value;
            
            initializeUsers(); // Garante que a lista de usuários 'users' esteja atualizada

            if (idade <= 0 || senha.length < 6 || users[nome]) {
                if (users[nome]) alert('Usuário já cadastrado (nome reservado)!');
                else alert('Dados inválidos: Idade deve ser positiva e Senha >= 6 caracteres.');
                return;
            }
            
            // NOVO: Adiciona a role padrão 'usuario'
            const pessoa = { nome, idade, senha, role: 'usuario' }; 
            let pessoas = JSON.parse(localStorage.getItem('pessoas')) || [];
            pessoas.push(pessoa);
            localStorage.setItem('pessoas', JSON.stringify(pessoas));
            
            // Adiciona a pessoa ao objeto 'users' em tempo real
            initializeUsers(); 
            updateListaPessoas();
            this.reset();
            alert(`Pessoa "${nome}" cadastrada com sucesso como usuário simples!`);
            
            if (currentUser && currentUser.role === 'admin') {
                updateNav();
            }
        });

        // 2. Fornecedores
        function updateListaFornecedores() {
            const fornecedores = JSON.parse(localStorage.getItem('fornecedores')) || [];
            document.getElementById('listaFornecedores').innerHTML = fornecedores.map(f => 
                `<li class="list-group-item">
                    <div>
                        <strong>${f.nome}</strong> | CNPJ: ${f.cnpj}
                    </div>
                    <small class="text-muted">Email: ${f.email || 'N/A'} | Telefone: ${f.telefone || 'N/A'}</small>
                </li>`
            ).join('');
        }

        document.getElementById('fornecedorForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const fornecedor = {
                nome: document.getElementById('nomeFornecedor').value,
                cnpj: document.getElementById('cnpjFornecedor').value,
                telefone: document.getElementById('telefoneFornecedor').value,
                email: document.getElementById('emailFornecedor').value
            };
            let fornecedores = JSON.parse(localStorage.getItem('fornecedores')) || [];
            if (fornecedores.some(f => f.cnpj === fornecedor.cnpj)) {
                alert('Erro: Já existe um fornecedor com este CNPJ!');
                return;
            }
            fornecedores.push(fornecedor);
            localStorage.setItem('fornecedores', JSON.stringify(fornecedores));
            updateListaFornecedores();
            this.reset();
            alert('Fornecedor cadastrado com sucesso!');
        });
        
        // 3. Produtos
        function updateListaProdutos() {
            const produtos = JSON.parse(localStorage.getItem('produtos')) || [];
            document.getElementById('listaProdutos').innerHTML = produtos.map(p => 
                `<li class="list-group-item ${p.quantidade < 10 ? 'border-danger' : ''}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${p.nome}</strong> (${p.codigo}) 
                            <span class="badge bg-secondary ms-2">${p.categoria}</span>
                        </div>
                        <div>
                            Qtd: <strong class="${p.quantidade < 10 ? 'text-danger' : 'text-success'}">${p.quantidade}</strong> 
                            | Preço: R$ ${p.preco.toFixed(2)}
                            ${p.quantidade < 10 ? '<span class="badge bg-danger ms-2">BAIXO ESTOQUE</span>' : ''}
                        </div>
                    </div>
                </li>`
            ).join('');
        }

        document.getElementById('produtoForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const codigo = document.getElementById('codigoProd').value.trim();
            let produtos = JSON.parse(localStorage.getItem('produtos')) || [];

            if (produtos.some(p => p.codigo === codigo)) {
                alert('Erro: Já existe um produto com este código!');
                return;
            }

            const produto = {
                nome: document.getElementById('nomeProd').value,
                codigo: codigo,
                categoria: document.getElementById('categoria').value,
                quantidade: parseInt(document.getElementById('quantidade').value),
                preco: parseFloat(document.getElementById('preco').value)
            };
            
            produtos.push(produto);
            localStorage.setItem('produtos', JSON.stringify(produtos));
            updateListaProdutos();
            this.reset();
            alert('Produto cadastrado com sucesso!');
            updateDashboardData();
        });

        // 4. Movimentações
        function registrarMovimentacao(codigo, tipo, quantidade) {
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

        document.getElementById('entradaForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const codigo = document.getElementById('codigoEntrada').value;
            const quantidade = parseInt(document.getElementById('quantidadeEntrada').value);
            let produtos = JSON.parse(localStorage.getItem('produtos')) || [];
            const produto = produtos.find(p => p.codigo === codigo);
            
            if (produto && quantidade > 0) {
                produto.quantidade += quantidade;
                localStorage.setItem('produtos', JSON.stringify(produtos));
                registrarMovimentacao(codigo, 'entrada', quantidade);
                alert(`Entrada de ${quantidade} unidades do produto ${codigo} registrada!`);
                updateListaProdutos();
                updateDashboardData();
            } else {
                alert(produto ? 'A quantidade deve ser positiva.' : 'Produto não encontrado!');
            }
            this.reset();
        });

        document.getElementById('saidaForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const codigo = document.getElementById('codigoSaida').value;
            const quantidade = parseInt(document.getElementById('quantidadeSaida').value);
            let produtos = JSON.parse(localStorage.getItem('produtos')) || [];
            const produto = produtos.find(p => p.codigo === codigo);

            if (produto && quantidade > 0) {
                if (produto.quantidade >= quantidade) {
                    produto.quantidade -= quantidade;
                    localStorage.setItem('produtos', JSON.stringify(produtos));
                    registrarMovimentacao(codigo, 'saida', quantidade);
                    alert(`Saída de ${quantidade} unidades do produto ${codigo} registrada!`);
                    updateListaProdutos();
                    updateDashboardData();
                } else {
                    alert(`Quantidade insuficiente! Estoque atual: ${produto.quantidade}.`);
                }
            } else {
                alert(produto ? 'A quantidade deve ser positiva.' : 'Produto não encontrado!');
            }
            this.reset();
        });


        // --- Consulta e Relatórios ---

        document.getElementById('consultaForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const tipo = document.getElementById('tipoConsulta').value;
            const valor = document.getElementById('valorConsulta').value.trim().toLowerCase();
            const produtos = JSON.parse(localStorage.getItem('produtos')) || [];
            let resultados = [];
            
            if (tipo === 'codigo' && valor) {
                resultados = produtos.filter(p => p.codigo.toLowerCase() === valor);
            } else if (tipo === 'categoria' && valor) {
                resultados = produtos.filter(p => p.categoria.toLowerCase() === valor);
            } else if (tipo === 'todos') {
                resultados = produtos;
            }

            const htmlResultado = resultados.length > 0
                ? resultados.map(p => 
                    `**${p.nome}** (${p.codigo}) | Categoria: ${p.categoria} | Qtd: **${p.quantidade}** | Preço: R$ ${p.preco.toFixed(2)}`
                ).join('<br>')
                : '<span class="text-muted">Nenhum resultado encontrado.</span>';

            document.getElementById('resultadoConsulta').innerHTML = htmlResultado;
        });

        document.getElementById('relatorioForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const tipo = document.getElementById('tipoRelatorio').value;
            const produtos = JSON.parse(localStorage.getItem('produtos')) || [];
            const movimentacoes = JSON.parse(localStorage.getItem('movimentacoes')) || [];
            let relatorio = [];
            
            if (tipo === 'baixo') {
                relatorio = produtos
                    .filter(p => p.quantidade < 10)
                    .map(p => `<span class="text-danger">⚠️ **${p.nome}** (${p.codigo}) - Qtd: **${p.quantidade}** (Necessita de reposição!)</span>`);
            } else if (tipo === 'movimentacoes') {
                relatorio = movimentacoes
                    .slice(-10) 
                    .reverse() 
                    .map(m => {
                        const style = m.tipo === 'entrada' ? 'text-success' : 'text-danger';
                        const icon = m.tipo === 'entrada' ? '⬆️' : '⬇️';
                        return `[${m.data}] | Tipo: <strong class="${style}">${icon} ${m.tipo.toUpperCase()}</strong> | Produto: ${m.codigo} | Qtd: ${m.quantidade} | Por: ${m.usuario}`;
                    });
            }
            
            const htmlRelatorio = relatorio.length > 0
                ? relatorio.join('<br>')
                : '<span class="text-muted">Nenhum dado encontrado para este relatório.</span>';

            document.getElementById('resultadoRelatorio').innerHTML = htmlRelatorio;
        });


        // --- Inicialização da Aplicação ---
        initializeUsers(); // Carrega usuários simples ao iniciar
        showPage('login'); // Começa na tela de login
        updateNav(); // Garante que a navegação esteja oculta
