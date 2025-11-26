from django.urls import path, include
from rest_framework import routers
from .views import (
    ProdutoViewSet, 
    FornecedorViewSet, 
    MovimentacaoEstoqueViewSet,
    UserViewSet # ✅ NOVO: Importando o UserViewSet
)

# 1. Definir o Roteador
router = routers.DefaultRouter()

# 2. Registrar todos os ViewSets, incluindo o de Usuários
router.register(r'users', UserViewSet) # <--- OBRIGATÓRIO: Adiciona a rota /users/
router.register(r'produtos', ProdutoViewSet)
router.register(r'fornecedores', FornecedorViewSet)
router.register(r'movimentacoes-estoque', MovimentacaoEstoqueViewSet)

# 3. Expor as rotas no URL principal
urlpatterns = [
    # Isso expõe /api/v1/users/, /api/v1/produtos/, etc.
    path('', include(router.urls)),
]