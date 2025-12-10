from rest_framework import serializers
from .models import Categoria, Fornecedor, Produto, MovimentacaoEstoque
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()

# ====================================================================
# SERIALIZERS DE AUTENTICAÇÃO E USUÁRIOS
# ====================================================================

class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'is_staff', 
            'is_superuser', 
            'date_joined',
            'last_login',
            'role_display'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_role_display(self, obj):
        """Retorna o nome da role em português"""
        if obj.is_superuser:
            return 'Administrador'
        elif obj.is_staff:
            return 'Gerente'
        else:
            return 'Atendente'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=6,
        error_messages={
            'min_length': 'A senha deve ter pelo menos 6 caracteres.'
        }
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password', 
            'password2', 
            'first_name', 
            'last_name'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        # Verifica se as senhas coincidem
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        
        # Verifica se o usuário já existe
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Este nome de usuário já está em uso."})
        
        # Verifica se o email já existe
        if attrs.get('email') and User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Este email já está registrado."})
        
        return attrs

    def create(self, validated_data):
        # Remove password2 dos dados validados
        validated_data.pop('password2')
        
        # Cria o usuário com permissões padrão
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=False,  # Novo usuário não é staff por padrão
            is_superuser=False  # Nunca criar superuser pelo registro público
        )
        
        # Define a senha (criptografada)
        user.set_password(validated_data['password'])
        user.save()
        return user

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=6,
        error_messages={
            'min_length': 'A senha deve ter pelo menos 6 caracteres.'
        }
    )
    
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password', 
            'first_name', 
            'last_name', 
            'is_staff', 
            'is_superuser'
        ]
        
    def validate(self, attrs):
        # Verifica se o usuário já existe
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Este nome de usuário já está em uso."})
        
        # Verifica se o email já existe
        if attrs.get('email') and User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Este email já está registrado."})
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=validated_data.get('is_staff', False),
            is_superuser=validated_data.get('is_superuser', False)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UpdateUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_staff', 'is_superuser']
        
    def validate(self, attrs):
        # Validações de segurança
        if attrs.get('is_superuser', False):
            # Verificar se o usuário que está fazendo a requisição tem permissão
            # Isso será feito na view
            pass
        return attrs

# ====================================================================
# SERIALIZERS DO APLICATIVO (ESTOQUE/LIVRARIA)
# ====================================================================

class CategoriaSerializer(serializers.ModelSerializer):
    total_produtos = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = [
            'id', 
            'nome', 
            'descricao', 
            'criado_em', 
            'atualizado_em', 
            'total_produtos'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']
    
    def get_total_produtos(self, obj):
        return obj.produtos.count()

class FornecedorSerializer(serializers.ModelSerializer):
    total_produtos = serializers.SerializerMethodField()
    
    class Meta:
        model = Fornecedor
        fields = [
            'id', 
            'nome', 
            'telefone', 
            'email', 
            'endereco', 
            'cnpj', 
            'contato', 
            'ativo', 
            'criado_em', 
            'atualizado_em', 
            'total_produtos'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']
    
    def get_total_produtos(self, obj):
        return obj.produtos.count()

class ProdutoSerializer(serializers.ModelSerializer):
    # Campos relacionados (para exibição)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    fornecedor_nome = serializers.CharField(source='fornecedor.nome', read_only=True, allow_null=True)
    
    # Campos calculados
    valor_total_estoque = serializers.SerializerMethodField()
    estoque_baixo = serializers.SerializerMethodField()
    margem_lucro = serializers.SerializerMethodField()
    
    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'descricao',
            'preco_custo',
            'preco_venda',
            'categoria',
            'categoria_nome',
            'fornecedor',
            'fornecedor_nome',
            'codigo_barras',
            'quantidade_estoque',
            'estoque_minimo',
            'ativo',
            'criado_em',
            'atualizado_em',
            'valor_total_estoque',
            'estoque_baixo',
            'margem_lucro'
        ]
        read_only_fields = ['criado_em', 'atualizado_em', 'valor_total_estoque', 'estoque_baixo', 'margem_lucro']
    
    def get_valor_total_estoque(self, obj):
        """Calcula o valor total em estoque (quantidade x preço de custo)"""
        return obj.quantidade_estoque * obj.preco_custo
    
    def get_estoque_baixo(self, obj):
        """Verifica se o estoque está abaixo do mínimo"""
        return obj.quantidade_estoque < obj.estoque_minimo
    
    def get_margem_lucro(self, obj):
        """Calcula a margem de lucro em porcentagem"""
        if obj.preco_custo > 0:
            return round(((obj.preco_venda - obj.preco_custo) / obj.preco_custo) * 100, 2)
        return 0
    
    def validate(self, data):
        """Validações customizadas"""
        # Verifica se preço de venda é maior que preço de custo
        preco_custo = data.get('preco_custo', self.instance.preco_custo if self.instance else 0)
        preco_venda = data.get('preco_venda', self.instance.preco_venda if self.instance else 0)
        
        if preco_venda < preco_custo:
            raise serializers.ValidationError({
                'preco_venda': 'O preço de venda não pode ser menor que o preço de custo.'
            })
        
        # Verifica se estoque mínimo é positivo
        estoque_minimo = data.get('estoque_minimo', self.instance.estoque_minimo if self.instance else 0)
        if estoque_minimo < 0:
            raise serializers.ValidationError({
                'estoque_minimo': 'O estoque mínimo não pode ser negativo.'
            })
        
        return data

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    # Campos relacionados (para exibição)
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # Campos calculados
    valor_total = serializers.SerializerMethodField()
    
    class Meta:
        model = MovimentacaoEstoque
        fields = [
            'id', 
            'produto', 
            'produto_nome', 
            'tipo', 
            'tipo_display',
            'quantidade', 
            'data_hora', 
            'usuario', 
            'usuario_nome',
            'motivo',
            'numero_documento',
            'observacao',
            'valor_total',
            'saldo_anterior'
        ]
        read_only_fields = ['data_hora', 'usuario', 'valor_total']
    
    def get_valor_total(self, obj):
        """Calcula o valor total da movimentação"""
        return obj.quantidade * obj.produto.preco_custo
    
    def validate(self, data):
        """Validações customizadas para movimentações"""
        produto = data.get('produto') or (self.instance.produto if self.instance else None)
        quantidade = data.get('quantidade', 0)
        tipo = data.get('tipo', '')
        
        if produto and tipo == 'S':  # Saída
            if quantidade > produto.quantidade_estoque:
                raise serializers.ValidationError({
                    'quantidade': f'Estoque insuficiente. Disponível: {produto.quantidade_estoque}'
                })
        
        return data

class MovimentacaoActionSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'A quantidade deve ser maior que zero.',
            'required': 'A quantidade é obrigatória.'
        }
    )
    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255
    )
    numero_documento = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50
    )
    observacao = serializers.CharField(
        required=False,
        allow_blank=True
    )

# ====================================================================
# SERIALIZERS PARA RELATÓRIOS
# ====================================================================

class EstatisticasSerializer(serializers.Serializer):
    total_produtos = serializers.IntegerField()
    total_categorias = serializers.IntegerField()
    total_fornecedores = serializers.IntegerField()
    valor_total_estoque = serializers.DecimalField(max_digits=15, decimal_places=2)
    produtos_estoque_baixo = serializers.IntegerField()
    movimentacoes_hoje = serializers.IntegerField()
    total_usuarios = serializers.IntegerField()

class RelatorioVendasSerializer(serializers.Serializer):
    periodo_inicio = serializers.DateField()
    periodo_fim = serializers.DateField()
    total_vendas = serializers.IntegerField()
    valor_total_vendas = serializers.DecimalField(max_digits=15, decimal_places=2)
    produto_mais_vendido = serializers.CharField()
    categoria_mais_vendida = serializers.CharField()

# ====================================================================
# SERIALIZERS PARA DASHBOARD
# ====================================================================

class DashboardStatsSerializer(serializers.Serializer):
    titulos_acervo = serializers.IntegerField()
    exemplares_estoque = serializers.IntegerField()
    titulos_falta = serializers.IntegerField()
    valor_total_acervo = serializers.DecimalField(max_digits=15, decimal_places=2)
    livros_mais_vendidos = serializers.ListField(child=serializers.DictField())
    generos_mais_populares = serializers.ListField(child=serializers.DictField())

# ====================================================================
# SERIALIZERS PARA VALIDAÇÃO DE FORMULÁRIOS
# ====================================================================

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=6
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "As senhas não coincidem."})
        return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=6
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "As senhas não coincidem."})
        return attrs