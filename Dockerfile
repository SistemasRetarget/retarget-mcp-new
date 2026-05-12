FROM node:20-slim

WORKDIR /app

# Crear un simple servidor HTTP en Node.js
RUN cat > server.js << 'EOF'
const http = require('http');

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({status: 'healthy'}));
  } else if (req.url.match(/^\/api\/v1\/context\/\d+$/)) {
    const userId = req.url.split('/').pop();
    res.writeHead(200, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({
      user_id: userId,
      context: {
        tasks: [],
        communications: [],
        calendar: [],
        projects: [],
        metrics: { productivity: 0 }
      }
    }));
  } else {
    res.writeHead(404, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({error: 'Not Found'}));
  }
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
EOF

EXPOSE 8080

CMD ["node", "server.js"]
