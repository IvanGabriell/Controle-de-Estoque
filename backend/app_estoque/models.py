from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    # CNPJ deve aceitar nulo se não informado, para não dar erro de duplicidade em campos vazios
    cnpj = models.CharField(max_length=18, blank=True, null=True, unique=True)
    contato = models.CharField(max_length=100, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        related_name="produtos",
        blank=True,
        null=True
    )
    
    codigo_barras = models.CharField(max_length=50, blank=True, null=True, unique=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.quantidade_estoque} em estoque)"
    
    def clean(self):
        """Validação personalizada"""
        if self.preco_venda < self.preco_custo:
            raise ValidationError('O preço de venda não pode ser menor que o preço de custo')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def lucro(self):
        return self.preco_venda - self.preco_custo
    
    @property
    def margem_lucro(self):
        if self.preco_custo > 0:
            return round(((self.preco_venda - self.preco_custo) / self.preco_custo) * 100, 2)
        return 0
    
    @property
    def estoque_baixo(self):
        return self.quantidade_estoque < self.estoque_minimo

class MovimentacaoEstoque(models.Model):
    class TipoMovimentacao(models.TextChoices):
        ENTRADA = 'E', 'Entrada'
        SAIDA = 'S', 'Saída'
        AJUSTE = 'A', 'Ajuste'
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=1, choices=TipoMovimentacao.choices)
    quantidade = models.PositiveIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    
    saldo_anterior = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.produto.nome} ({self.quantidade})"

    def clean(self):
        """Validação antes de salvar: Impede saída se não tiver estoque"""
        if self.tipo == 'S' and self.quantidade > self.produto.quantidade_estoque:
            raise ValidationError(f'Estoque insuficiente. Disponível: {self.produto.quantidade_estoque}')

    def save(self, *args, **kwargs):
        self.clean() # Chama validação
        
        if not self.pk: # Apenas se for criação nova
            self.saldo_anterior = self.produto.quantidade_estoque
            
            if self.tipo == 'E':
                self.produto.quantidade_estoque += self.quantidade
            elif self.tipo == 'S':
                # A validação já ocorreu no clean(), mas por segurança:
                if self.produto.quantidade_estoque >= self.quantidade:
                    self.produto.quantidade_estoque -= self.quantidade
            elif self.tipo == 'A':
                self.produto.quantidade_estoque = self.quantidade
            
            self.produto.save()
        
        super().save(*args, **kwargs)