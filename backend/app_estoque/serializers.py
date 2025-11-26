from rest_framework import serializers
from .models import Categoria, Fornecedor, Produto, MovimentacaoEstoque
from django.contrib.auth import get_user_model

User = get_user_model()

# ====================================================================
# NOVO: USER SERIALIZER (CRÍTICO PARA EXPOR AS PERMISSÕES)
# ====================================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # CRÍTICO: Expor is_staff e is_superuser para mapear a role no Frontend
        fields = ('id', 'username', 'email', 'is_staff', 'is_superuser') 
# ====================================================================


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__' 

class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = '__all__' 

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

# 1. Serializer para visualização e listagem (Read-Only)
class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    # Campo para exibir o nome de usuário (leitura)
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True) 

    class Meta:
        model = MovimentacaoEstoque
        # Garante que o campo extra seja incluído e que campos sensíveis sejam read-only
        fields = ['id', 'produto', 'tipo', 'quantidade', 'data_hora', 'usuario', 'usuario_nome']
        read_only_fields = ['usuario', 'tipo', 'data_hora']

# 2. Serializer para a ação de Entrada/Saída (Write-Only)
class MovimentacaoActionSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(min_value=1)