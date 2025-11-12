from rest_framework import serializers
from .models import Categoria, Fornecedor, Produto, MovimentacaoEstoque

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__' #Vai serializar todos os campos do modelo Categoria

class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = '__all__' 

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimentacaoEstoque
        fields = '__all__'

class MovimentacaoEstoqueDetailSerializer(serializers.ModelSerializer):
    quantidade = serializers.IntegerField()

class MovimentacaoActionSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(min_value=1)