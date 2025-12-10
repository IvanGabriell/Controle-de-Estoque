from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # ViewSets existentes
    ProdutoViewSet, 
    FornecedorViewSet, 
    MovimentacaoEstoqueViewSet,
    UserViewSet,
    CategoriaViewSet,
    
    # Novas views de autenticação
    CustomTokenObtainPairView,
    register_view,
    create_user_admin,
    list_all_users,
    update_user_role,
    delete_user,
    me_view,
    
    # Views de teste e utilitários
    health_check,
    test_cors,
    estatisticas_view,
    
    # Views de gerenciamento
    estatisticas_view
)

# 1. Definir o Roteador
router = routers.DefaultRouter()

# 2. Registrar todos os ViewSets
router.register(r'users', UserViewSet, basename='user')
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'fornecedores', FornecedorViewSet, basename='fornecedor')
router.register(r'movimentacoes', MovimentacaoEstoqueViewSet, basename='movimentacao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

# 3. Expor as rotas no URL principal
urlpatterns = [
    # Rotas da API via router
    path('', include(router.urls)),
    
    # ==========================================================================
    # AUTENTICAÇÃO E USUÁRIOS
    # ==========================================================================
    
    # Login com JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registro público (qualquer um pode se registrar)
    path('register/', register_view, name='register'),
    
    # Informações do usuário atual
    path('me/', me_view, name='me'),
    
    # ==========================================================================
    # GERENCIAMENTO DE USUÁRIOS (APENAS ADMIN)
    # ==========================================================================
    
    # Criar usuário (apenas admin)
    path('users/create/admin/', create_user_admin, name='create_user_admin'),
    
    # Listar todos os usuários (apenas admin)
    path('users/list/all/', list_all_users, name='list_all_users'),
    
    # Atualizar role/permissões de um usuário (apenas admin)
    path('users/<int:user_id>/update-role/', update_user_role, name='update_user_role'),
    
    # Deletar usuário (apenas admin)
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),
    
    # ==========================================================================
    # TESTES E MONITORAMENTO
    # ==========================================================================
    
    # Health check (público)
    path('health/', health_check, name='health_check'),
    
    # Teste de CORS (público)
    path('test-cors/', test_cors, name='test_cors'),
    
    # ==========================================================================
    # RELATÓRIOS E ESTATÍSTICAS
    # ==========================================================================
    
    # Estatísticas do sistema
    path('estatisticas/', estatisticas_view, name='estatisticas'),
    
    # ==========================================================================
    # ENDPOINTS ESPECÍFICOS DOS PRODUTOS (AÇÕES CUSTOMIZADAS)
    # ==========================================================================
    
    # Entrada de estoque para um produto específico
    path('produtos/<int:pk>/entrada/', 
         ProdutoViewSet.as_view({'post': 'dar_entrada'}), 
         name='produto-entrada'),
    
    # Saída de estoque para um produto específico
    path('produtos/<int:pk>/saida/', 
         ProdutoViewSet.as_view({'post': 'dar_saida'}), 
         name='produto-saida'),
    
    # Listar produtos com estoque baixo
    path('produtos/estoque-baixo/', 
         ProdutoViewSet.as_view({'get': 'estoque_baixo'}), 
         name='produto-estoque-baixo'),
    
    # ==========================================================================
    # ENDPOINTS ESPECÍFICOS DOS FORNECEDORES
    # ==========================================================================
    
    # Listar apenas fornecedores ativos
    path('fornecedores/ativos/', 
         FornecedorViewSet.as_view({'get': 'ativos'}), 
         name='fornecedores-ativos'),
]