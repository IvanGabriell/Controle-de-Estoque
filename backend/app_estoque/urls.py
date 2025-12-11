from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

# Importando todas as views corretamente
from .views import (
    # ViewSets (Lógica padrão CRUD)
    ProdutoViewSet, 
    FornecedorViewSet, 
    MovimentacaoEstoqueViewSet,
    UserViewSet,
    CategoriaViewSet,
    
    # Views de Autenticação e Usuários (Personalizadas)
    CustomTokenObtainPairView, # A classe que corrigimos
    register_view,
    create_user_admin,
    list_all_users,
    update_user_role,
    delete_user,
    me_view,
    
    # Utilitários e Relatórios
    health_check,
    test_cors,
    estatisticas_view
)

# 1. Definir o Roteador (Gera as rotas padrões automaticamente)
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'fornecedores', FornecedorViewSet, basename='fornecedor')
router.register(r'movimentacoes', MovimentacaoEstoqueViewSet, basename='movimentacao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

# 2. Definir as Rotas
urlpatterns = [
    # ==========================================================================
    # ROTAS ESPECÍFICAS DE USUÁRIOS (Devem vir ANTES do router)
    # ==========================================================================
    # Estas rotas batem exatamente com o fetch do seu JavaScript novo
    
    path('users/admin-create/', create_user_admin, name='create_user_admin'),
    path('users/all/', list_all_users, name='list_all_users'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user_custom'),
    path('users/<int:user_id>/update-role/', update_user_role, name='update_user_role'),
    
    # ==========================================================================
    # AUTENTICAÇÃO (Login e Registro)
    # ==========================================================================
    
    # Login: Retorna o Token JWT (Usa a view corrigida)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Refresh: Renova o token quando expira
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Registro Público
    path('register/', register_view, name='register'),
    # Dados do usuário logado
    path('me/', me_view, name='me'),

    # ==========================================================================
    # ROTAS PADRÃO DO ROUTER (ViewSets)
    # ==========================================================================
    # Isso cuida de /users/, /users/1/, /produtos/, etc.
    path('', include(router.urls)),

    # ==========================================================================
    # UTILITÁRIOS E MONITORAMENTO
    # ==========================================================================
    path('health/', health_check, name='health_check'),
    path('test-cors/', test_cors, name='test_cors'),
    path('estatisticas/', estatisticas_view, name='estatisticas'),

    # ==========================================================================
    # AÇÕES PERSONALIZADAS DE PRODUTOS
    # ==========================================================================
    path('produtos/<int:pk>/entrada/', 
         ProdutoViewSet.as_view({'post': 'dar_entrada'}), 
         name='produto-entrada'),
    
    path('produtos/<int:pk>/saida/', 
         ProdutoViewSet.as_view({'post': 'dar_saida'}), 
         name='produto-saida'),
    
    path('produtos/estoque-baixo/', 
         ProdutoViewSet.as_view({'get': 'estoque_baixo'}), 
         name='produto-estoque-baixo'),

    # ==========================================================================
    # AÇÕES PERSONALIZADAS DE FORNECEDORES
    # ==========================================================================
    path('fornecedores/ativos/', 
         FornecedorViewSet.as_view({'get': 'ativos'}), 
         name='fornecedores-ativos'),
]