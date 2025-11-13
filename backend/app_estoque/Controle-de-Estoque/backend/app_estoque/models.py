from django.db import models
from django.conf import settings

#Isso são categorias, por exemplo: Limpeza, Escritório, Informática, etc...
class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome
    
#Criando agora o dos fornencedores:
class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self):
        return self.nome
    
class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    categoria = models.ForeignKey(
            Categoria,
            on_delete=models.PROTECT, #impede o apagamento da categoria caso tenha produtos vinculados a ela
            related_name="produtos"
        )
    fornecedor = models.ForeignKey(
            Fornecedor,
            on_delete=models.PROTECT, #impede o apagamento do fornecedor caso tenha produtos vinculados a ele
            related_name="produtos",
            blank=True,
            null=True
        )

    quantidade_estoque = models.PositiveIntegerField(default=0)

    class Meta:
            verbose_name = "Produto"
            verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome} ({self.quantidade_estoque} em estoque)"
    
#MovimentaçãoEstoque: Registra entradas e saídas de produtos no estoque
class MovimentacaoEstoque(models.Model):

    class TipoMovimentacao(models.TextChoices):
        ENTRADA = 'E', 'Entrada'
        SAIDA = 'S', 'Saída'

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

    #Agora quem faz a movimentação do estoque é o usuário autenticado
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, #Isso mantem o histórico
        null=True,
        blank=True #Permite movimentações automáticas sem um usuário específico
        )
    
    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_hora'] #Ordena da mais recente para a mais antiga

        def __str__(self):
            tipo_str = self.get_tipo_display() #Pega a representação legível do tipo
            return f"{tipo_str} de {self.quantidade}x {self.produto.nome} em {self.data_hora.strftime('%d/%m/%Y')}"