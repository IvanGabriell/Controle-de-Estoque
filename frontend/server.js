// server.js - Colocar na pasta frontend!
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

const server = http.createServer((req, res) => {
    console.log(`📄 Acessando: ${req.url}`);
    
    // Define o arquivo baseado na URL
    let filePath = '.' + req.url;
    if (filePath === './') {
        filePath = './index.html';
    }
    
    // Verifica a extensão para definir Content-Type
    const extname = path.extname(filePath);
    let contentType = 'text/html';
    
    switch (extname) {
        case '.js':
            contentType = 'text/javascript';
            break;
        case '.css':
            contentType = 'text/css';
            break;
        case '.json':
            contentType = 'application/json';
            break;
        case '.png':
            contentType = 'image/png';
            break;
        case '.jpg':
            contentType = 'image/jpg';
            break;
        case '.ico':
            contentType = 'image/x-icon';
            break;
    }
    
    // Lê e serve o arquivo
    fs.readFile(filePath, (error, content) => {
        if (error) {
            if(error.code === 'ENOENT') {
                // Página não encontrada - tenta servir index.html
                fs.readFile('./index.html', (error, content) => {
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end(content, 'utf-8');
                });
            } else {
                // Erro do servidor
                res.writeHead(500);
                res.end(`Desculpe, erro no servidor: ${error.code}`);
            }
        } else {
            // Sucesso
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(PORT, () => {
    console.log(`
    🚀 SERVIDOR FRONTEND LOCAL INICIADO!
    =====================================
    📍 URL: http://localhost:${PORT}
    📁 Pasta: ${__dirname}
    
    🔗 URLs importantes:
       • Login:        http://localhost:${PORT}/
       • Dashboard:    http://localhost:${PORT}/dashboard.html
    
    ⚠️  IMPORTANTE: Certifique-se de que:
       • Backend Django está rodando em: http://localhost:8000
       • Comando: python manage.py runserver 0.0.0.0:8000
    
    Pressione Ctrl+C para parar o servidor.
    `);
});