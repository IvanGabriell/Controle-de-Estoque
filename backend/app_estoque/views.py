from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import F #atualizações
from django.db import transaction #Transições

from .models import Categoria, Fornecedor, Produto, MovimentacaoEstoque
from .serializers import (
    CategoriaSerializer,
    FornecedorSerializer,
    ProdutoSerializer,
    MovimentacaoEstoqueSerializer,
    MovimentacaoActionSerializer 
)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _realizar_movimentacao(self, request, pk, tipo_movimentacao):
        """
        Função auxiliar para realizar movimentações de estoque.
        Garante que o estoque seja atualizado corretamente
        """
        produto = self.get_object() #pega o produto

        serializer = MovimentacaoActionSerialLizer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quantidade = serializer.validated_data['quantidade']

        try:
            #Transação atômica para garantir integridade dos dados
            #Se ocorrer um erro, todas as operações serão revertidas
            with transaction.atomic():
                #Atualiza o estoque do produto
               
                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo=tipo_movimentacao,
                    quantidade=quantidade,
                    usuario=request.user #Graças a mim aqui :) validaão do usuário
                )
                
                if tipo_movimentacao == MovimentacaoEstoque.TipoMovimentacao.ENTRADA:
                    #Usar F() para evitar condições de corrida
                    produto.quantidade_estoque = F('quantidade_estoque') + quantidade
                else: #SAIDA
                    if produto.quantidade_estoque < quantidade:
                        raise ValueError("Estoque insuficiente para a saída solicitada.")
                    produto.quantidade_estoque = F('quantidade_estoque') - quantidade
                
                produto.save()
                produto.refresh_from_db() #Atualiza o objeto produto com o valor mais recente do banco de dados
                
                produto_serializer = self.get_serializer(produto)
                return Response(produto_serializer.data, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            #Erro específico de validação
            return Response({"detalhe": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            #Erro genérico
            return Response({"detalhe": "Erro ao processar a movimentação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='dar-entrada')
    def dar_entrada(self, request, pk=None):
        """
        Endpoint personalizado para adicionar estoque a um produto.
        URL: /api/v1/produtos/1/dar-entrada/
        Body: {"quantidade": 10}
        """
        return self._realizar_movimentacao(request, pk, MovimentacaoEstoque.TipoMovimentacao.ENTRADA)

    @action(detail=True, methods=['post'], url_path='dar-saida')
    def dar_saida(self, request, pk=None):
        """
        Endpoint personalizado para remover estoque de um produto.
        URL: /api/v1/produtos/1/dar-saida/
        Body: {"quantidade": 5}
        """
        return self._realizar_movimentacao(request, pk, MovimentacaoEstoque.TipoMovimentacao.SAIDA)

class MovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoEstoque.objects.all()
    serializer_class = MovimentacaoEstoqueSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
