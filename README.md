# 🚀 Sistema de Controle de Estoque (Back-End)


## 🏛️ Arquitetura e Tecnologias

* **Linguagem:** Python
* **Frameworks:** Django, Django REST Framework
* **Segurança:** Autenticação via Token Nativo (utilizado) e compatibilidade com JWT (configurado no código).
* **Banco de Dados:** SQLite (Desenvolvimento)

## ⚙️ Setup e Como Rodar (Passo a Passo Essencial)

**Atenção:** Assegure-se de que o terminal esteja na pasta `backend/` para comandos que usam `manage.py`.

### 1. Preparação do Ambiente
1.  Entre na pasta backend:
    ```bash
    cd backend
    ```
2.  Crie e ative o ambiente virtual (venv):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Instale as dependências:
    ```bash
    pip install django djangorestframework djangorestframework-simplejwt
    ```

### 2. Inicialização e Teste
1.  Execute as migrações (cria as tabelas no db.sqlite3):
    ```bash
    python manage.py migrate
    ```
2.  Crie um usuário administrador para testes no Admin e Login:
    ```bash
    python manage.py createsuperuser
    ```
3.  Inicie o servidor:
    ```bash
    python manage.py runserver
    ```

---

## 🔗 Endpoints da API (O Contrato Final)

O prefixo principal para a API é `/api/v1/`.

| Funcionalidade | Método | Endpoint | Descrição |
| :--- | :--- | :--- | :--- |
| **Login (Auth)** | `POST` | `/api/v1/login/` | Obtém o Token de Acesso (para usar no Header Authorization). |
| **Listar/Criar** | `GET`/`POST` | `/api/v1/produtos/` | CRUD básico para gerenciamento de produtos. |
| **Dar Entrada** | `POST` | `/api/v1/produtos/{id}/dar-entrada/` | Lógica de Negócio: Adiciona estoque e registra a transação de forma atômica (Fase 4). |
| **Dar Saída** | `POST` | `/api/v1/produtos/{id}/dar-saida/` | Lógica de Negócio: Remove estoque e verifica se o saldo é suficiente. |

**Teste de Acesso:** Para usar os *endpoints* listados acima, o Front-End ou o Postman deve enviar o cabeçalho: `Authorization: Token [CÓDIGO_RECEBIDO_NO_LOGIN]`.