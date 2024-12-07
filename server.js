const express = require('express');
const app = express();
const port = 3000;

// Middleware
app.use(express.json());
app.use(express.static('frontend')); // Serves frontend files

// Add CORS headers if needed
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

// Routes
app.post('/scrape-review', (req, res) => {
    console.log('Received scrape request:', req.body);
    // Your scrape logic here
    res.json({ message: 'Endpoint working' });
});

app.post('/parse-review', (req, res) => {
    console.log('Received parse request:', req.body);
    // Your parse logic here
    res.json({ message: 'Endpoint working' });
});

// Error handling
app.use((req, res) => {
    console.log('404 for url:', req.url);
    res.status(404).send('Not Found');
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
}); 