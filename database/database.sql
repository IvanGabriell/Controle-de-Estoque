-- Cria o banco de dados (se você ainda não o criou)
CREATE DATABASE IF NOT EXISTS controle_estoque;

-- Usa o banco de dados
USE controle_estoque;

-- 1. Tabela Categoria
-- (Criada primeiro, pois 'produto' depende dela)
CREATE TABLE categoria (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nome VARCHAR(100) NOT NULL UNIQUE
);

-- 2. Tabela Fornecedor
-- (Criada primeiro, pois 'produto' depende dela)
CREATE TABLE fornecedor (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255) UNIQUE
);

-- 3. Tabela Usuario
-- (Pode ser criada a qualquer momento, mas 'movimentacaoEstoque' depende dela)
CREATE TABLE usuario (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    -- Lembre-se de NUNCA salvar a senha como texto puro.
    -- Salve sempre um HASH da senha.
    senha VARCHAR(255) NOT NULL 
);

-- 4. Tabela Produto
-- (Depende de 'categoria' e 'fornecedor')
CREATE TABLE produto (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    nome VARCHAR(255) NOT NULL UNIQUE,
    descricao TEXT,
    preco_custo DECIMAL(10, 2) DEFAULT 0.00,
    preco_venda DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Coluna para o saldo atual do estoque
    quantidade_atual INT NOT NULL DEFAULT 0,
    
    -- Chaves estrangeiras (Relacionamentos)
    id_categoria INT,
    id_fornecedor INT,
    
    FOREIGN KEY (id_categoria) REFERENCES categoria(id),
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor(id)
);

-- 5. Tabela MovimentacaoEstoque
-- (Depende de 'produto' e 'usuario')
CREATE TABLE movimentacaoEstoque (
    id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    
    -- 'E' para Entrada, 'S' para Saída
    tipoMovimentacao ENUM('E', 'S') NOT NULL, 
    
    quantidade INT NOT NULL,
    
    -- Coluna para registrar QUANDO a movimentação ocorreu
    data_movimentacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Chaves estrangeiras (Relacionamentos)
    id_produto INT NOT NULL,
    id_usuario INT NOT NULL,
    
    FOREIGN KEY (id_produto) REFERENCES produto(id),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
);

-- 6. Trigger para atualizar o estoque automaticamente
-- Sempre que uma nova movimentação for inserida
DELIMITER $$

CREATE TRIGGER tg_atualizar_estoque
AFTER INSERT ON movimentacaoEstoque
FOR EACH ROW
BEGIN
    
    IF NEW.tipoMovimentacao = 'E' THEN
        -- Se for Entrada, SOMA a quantidade no produto
        UPDATE produto 
        SET quantidade_atual = quantidade_atual + NEW.quantidade
        WHERE id = NEW.id_produto;
        
    ELSEIF NEW.tipoMovimentacao = 'S' THEN
        -- Se for Saída, SUBTRAI a quantidade no produto
        UPDATE produto 
        SET quantidade_atual = quantidade_atual - NEW.quantidade
        WHERE id = NEW.id_produto;
    END IF;
END$$

DELIMITER ;