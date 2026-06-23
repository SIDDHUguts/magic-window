const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;

http.createServer((req, res) => {
    // Resolve clean files
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : req.url);
    
    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('File not found');
        } else {
            let contentType = 'text/html';
            if (filePath.endsWith('.js')) {
                contentType = 'text/javascript';
            } else if (filePath.endsWith('.css')) {
                contentType = 'text/css';
            }
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
}).listen(PORT, () => {
    console.log(`\n  ✦  SAmaniacLabs Server is live`);
    console.log(`     ↳ http://localhost:${PORT}\n`);
});
