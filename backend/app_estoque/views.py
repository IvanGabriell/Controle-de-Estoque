from rest_framework import viewsets, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from django.db.models import F
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import Categoria, Fornecedor, Produto, MovimentacaoEstoque
from .serializers import (
    CategoriaSerializer,
    FornecedorSerializer,
    ProdutoSerializer,
    MovimentacaoEstoqueSerializer,
    MovimentacaoActionSerializer,
    UserSerializer
)

# ==============================================================================
# VIEWS DE AUTENTICAÇÃO E USUÁRIOS
# ==============================================================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id') 
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Apenas superusers podem ver todos os usuários
        if self.request.user.is_superuser:
            return User.objects.all()
        # Usuários normais veem apenas a si mesmos
        return User.objects.filter(id=self.request.user.id)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Registro de novos usuários (público)"""
    from .serializers import RegisterSerializer
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user_admin(request):
    """Cria um novo usuário (apenas para administradores)"""
    # Verifica se é administrador
    if not request.user.is_superuser:
        return Response(
            {'error': 'Acesso negado. Apenas administradores podem criar usuários.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    is_staff = request.data.get('is_staff', False)
    is_superuser = request.data.get('is_superuser', False)
    
    # Validações
    if not username or not password:
        return Response(
            {'error': 'Username e password são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verifica se usuário já existe
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Usuário já existe'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Segurança: não permitir criar outro superuser
    if is_superuser and not request.user.is_superuser:
        return Response(
            {'error': 'Não autorizado a criar administradores'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Cria o usuário
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        # Define a senha (criptografada)
        user.set_password(password)
        user.save()
        
        # Retorna dados do usuário criado
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_users(request):
    """Lista todos os usuários (apenas para administradores)"""
    # Verifica se é administrador
    if not request.user.is_superuser:
        return Response(
            {'error': 'Acesso negado. Apenas administradores podem listar todos os usuários.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = User.objects.all().order_by('id')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_role(request, user_id):
    """Atualiza permissões de um usuário (apenas administradores)"""
    # Verifica se é administrador
    if not request.user.is_superuser:
        return Response(
            {'error': 'Acesso negado. Apenas administradores podem atualizar roles.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Busca usuário (não pode editar a si mesmo)
        user = User.objects.get(id=user_id)
        
        if user.id == request.user.id:
            return Response(
                {'error': 'Não é possível editar suas próprias permissões'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Atualiza permissões
        is_staff = request.data.get('is_staff', user.is_staff)
        is_superuser = request.data.get('is_superuser', user.is_superuser)
        
        # Segurança adicional
        if is_superuser and not request.user.is_superuser:
            return Response(
                {'error': 'Não autorizado a criar administradores'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        
        serializer = UserSerializer(user)
        return Response(serializer.data)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """Remove um usuário (apenas administradores)"""
    # Verifica se é administrador
    if not request.user.is_superuser:
        return Response(
            {'error': 'Acesso negado. Apenas administradores podem remover usuários.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Busca usuário (não pode deletar a si mesmo)
        user = User.objects.get(id=user_id)
        
        if user.id == request.user.id:
            return Response(
                {'error': 'Não é possível remover sua própria conta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user.username
        user.delete()
        
        return Response(
            {'message': f'Usuário {username} removido com sucesso'},
            status=status.HTTP_200_OK
        )
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Usuário não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Retorna informações do usuário atual"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint para verificar se a API está funcionando"""
    from django.utils import timezone
    return Response({
        'status': 'online',
        'message': 'API Controle de Estoque está funcionando!',
        'timestamp': timezone.now().isoformat(),
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def test_cors(request):
    """Endpoint para testar CORS"""
    return Response({
        'message': 'CORS está configurado corretamente!',
        'request_origin': request.headers.get('Origin', 'Não informado'),
    })

# ==============================================================================
# VIEWSETS DO APLICATIVO
# ==============================================================================

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
    
    @action(detail=False, methods=['get'])
    def ativos(self, request):
        """Lista apenas fornecedores ativos"""
        fornecedores = Fornecedor.objects.filter(ativo=True)
        serializer = self.get_serializer(fornecedores, many=True)
        return Response(serializer.data)

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtra produtos ativos por padrão"""
        queryset = super().get_queryset()
        ativo = self.request.query_params.get('ativo', 'true')
        if ativo.lower() == 'true':
            queryset = queryset.filter(ativo=True)
        return queryset
    
    @action(detail=False, methods=['get'])
    def estoque_baixo(self, request):
        """Lista produtos com estoque abaixo do mínimo"""
        from django.db.models import F
        produtos = Produto.objects.filter(
            quantidade_estoque__lt=F('estoque_minimo'),
            ativo=True
        )
        serializer = self.get_serializer(produtos, many=True)
        return Response(serializer.data)

    def _realizar_movimentacao(self, request, pk, tipo_movimentacao_const):
        """Função auxiliar para realizar movimentações de estoque"""
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
        except Exception as e:
            return Response(
                {"detalhe": f"Erro interno ao processar a movimentação: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='dar-entrada')
    def dar_entrada(self, request, pk=None):
        return self._realizar_movimentacao(request, pk, MovimentacaoEstoque.TipoMovimentacao.ENTRADA)

    @action(detail=True, methods=['post'], url_path='dar-saida')
    def dar_saida(self, request, pk=None):
        return self._realizar_movimentacao(request, pk, MovimentacaoEstoque.TipoMovimentacao.SAIDA)

class MovimentacaoEstoqueViewSet(viewsets.ModelViewSet):
    queryset = MovimentacaoEstoque.objects.all().order_by('-data_hora')
    serializer_class = MovimentacaoEstoqueSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra por produto se fornecido"""
        queryset = super().get_queryset()
        produto_id = self.request.query_params.get('produto')
        if produto_id:
            queryset = queryset.filter(produto_id=produto_id)
        return queryset
    
    def perform_create(self, serializer):
        """Associa o usuário atual à movimentação"""
        serializer.save(usuario=self.request.user)

# ==============================================================================
# VIEWS DE RELATÓRIOS
# ==============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estatisticas_view(request):
    """Retorna estatísticas gerais do sistema"""
    from django.db.models import Count, Sum
    from django.utils import timezone
    
    hoje = timezone.now().date()
    
    total_produtos = Produto.objects.filter(ativo=True).count()
    total_categorias = Categoria.objects.count()
    total_fornecedores = Fornecedor.objects.filter(ativo=True).count()
    
    # Calcula valor total do estoque
    produtos = Produto.objects.filter(ativo=True)
    valor_total_estoque = sum(p.quantidade_estoque * p.preco_custo for p in produtos)
    
    # Produtos com estoque baixo
    from django.db.models import F
    produtos_estoque_baixo = Produto.objects.filter(
        quantidade_estoque__lt=F('estoque_minimo'),
        ativo=True
    ).count()
    
    # Movimentações hoje
    movimentacoes_hoje = MovimentacaoEstoque.objects.filter(
        data_hora__date=hoje
    ).count()
    
    return Response({
        'total_produtos': total_produtos,
        'total_categorias': total_categorias,
        'total_fornecedores': total_fornecedores,
        'valor_total_estoque': valor_total_estoque,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'movimentacoes_hoje': movimentacoes_hoje,
    })