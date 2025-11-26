from rest_framework import viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import F
from django.db import transaction
from django.contrib.auth.models import User # Importação necessária para o queryset de usuários

from .models import Categoria, Fornecedor, Produto, MovimentacaoEstoque
from .serializers import (
    CategoriaSerializer,
    FornecedorSerializer,
    ProdutoSerializer,
    MovimentacaoEstoqueSerializer,
    MovimentacaoActionSerializer,
    UserSerializer # ✅ NOVO: Importando o Serializer de Usuário
)

# NOVO: ViewSet para listar e detalhar usuários (irá responder a /users/)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id') 
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
# --- SEUS VIEWSETS EXISTENTES ---

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _realizar_movimentacao(self, request, pk, tipo_movimentacao_const):
        """
        Função auxiliar para realizar movimentações de estoque.
        tipo_movimentacao_const: MovimentacaoEstoque.TipoMovimentacao.ENTRADA ou SAIDA
        """
        produto = self.get_object() 

        serializer = MovimentacaoActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quantidade = serializer.validated_data['quantidade']

        try:
            with transaction.atomic():
                
                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo=tipo_movimentacao_const,
                    quantidade=quantidade,
                    usuario=request.user
                )
                
                if tipo_movimentacao_const == MovimentacaoEstoque.TipoMovimentacao.ENTRADA:
                    produto.quantidade_estoque = F('quantidade_estoque') + quantidade
                else: # SAIDA
                    if produto.quantidade_estoque < quantidade:
                        raise ValueError("Estoque insuficiente para a saída solicitada.")
                    produto.quantidade_estoque = F('quantidade_estoque') - quantidade
                
                produto.save()
                produto.refresh_from_db()
                
                produto_serializer = self.get_serializer(produto)
                return Response(produto_serializer.data, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response({"detalhe": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detalhe": "Erro interno ao processar a movimentação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='dar-entrada')
    def dar_entrada(self, request, pk=None):
        return self._realizar_movimentacao(request, pk, MovimentacaoEstoque.TipoMovimentacao.ENTRADA)

    @action(detail=True, methods=['post'], url_path='dar-saida')
    def dar_saida(self, request, pk=None):
        return self._realizar_movimentacao(request, pk, MovimentacaoEstoque.TipoMovimentacao.SAIDA)

class MovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoEstoque.objects.all()
    serializer_class = MovimentacaoEstoqueSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]