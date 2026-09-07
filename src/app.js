const express = require('express');
const path = require('path');

const morgan = require('morgan');

const urlRoutes = require('./routes/url.routes');

const errorHandler = require('./middlewares/errorHandler');

const app = express();

app.use(morgan('dev'));

app.use(express.json());

app.use(express.static(path.join(__dirname, '..', 'public')));

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/', urlRoutes);

app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

app.use(errorHandler);

module.exports = app;