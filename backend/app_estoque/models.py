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
            raise ValidationError(
                'O preço de venda não pode ser menor que o preço de custo'
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def lucro(self):
        """Calcula o lucro unitário"""
        return self.preco_venda - self.preco_custo
    
    @property
    def margem_lucro(self):
        """Calcula a margem de lucro em %"""
        if self.preco_custo > 0:
            return round(((self.preco_venda - self.preco_custo) / self.preco_custo) * 100, 2)
        return 0
    
    @property
    def estoque_baixo(self):
        """Verifica se estoque está abaixo do mínimo"""
        return self.quantidade_estoque < self.estoque_minimo
    
    @property
    def valor_total_estoque(self):
        """Valor total em estoque (quantidade x preço_custo)"""
        return self.quantidade_estoque * self.preco_custo

class MovimentacaoEstoque(models.Model):
    class TipoMovimentacao(models.TextChoices):
        ENTRADA = 'E', 'Entrada'
        SAIDA = 'S', 'Saída'
        AJUSTE = 'A', 'Ajuste'
    
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='movimentacoes'
    )
    tipo = models.CharField(
        max_length=1,
        choices=TipoMovimentacao.choices
    )
    quantidade = models.PositiveIntegerField()
    data_hora = models.DateTimeField(auto_now_add=True)
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    motivo = models.CharField(max_length=255, blank=True, null=True)
    numero_documento = models.CharField(max_length=50, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    saldo_anterior = models.PositiveIntegerField(default=0)  # Saldo antes da movimentação
    
    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_hora']

    def __str__(self):
        tipo_str = self.get_tipo_display()
        return f"{tipo_str} de {self.quantidade}x {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        """Atualiza automaticamente o estoque do produto"""
        if not self.pk:  # Se for uma nova movimentação
            self.saldo_anterior = self.produto.quantidade_estoque
            
            # Atualiza estoque do produto
            if self.tipo == 'E':  # Entrada
                self.produto.quantidade_estoque += self.quantidade
            elif self.tipo == 'S':  # Saída
                if self.produto.quantidade_estoque >= self.quantidade:
                    self.produto.quantidade_estoque -= self.quantidade
                else:
                    raise ValidationError('Estoque insuficiente para saída')
            elif self.tipo == 'A':  # Ajuste
                self.produto.quantidade_estoque = self.quantidade
            
            self.produto.save()
        
        super().save(*args, **kwargs)