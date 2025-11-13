from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, FornecedorViewSet, ProdutoViewSet, MovimentacaoEstoqueViewSet

#Essa aqui vai para registrar as rotas automaticamente
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'fornecedores', FornecedorViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'movimentacoes-estoque', MovimentacaoEstoqueViewSet)

urlpatterns = [
    #Essa caçamba vai juntar todas as rotas que criamos no router
    path ('', include(router.urls)),
]