const express = require('express');
const cors = require('cors');
const session = require('express-session');

const app = express();
app.use(express.json());
app.use(cors({ origin: '*', credentials: true }));
app.use(session({ secret: 'keyboard-cat', resave: false, saveUninitialized: false }));

app.use('/auth', require('./routes/auth'));
app.use('/customers', require('./routes/customers'));
app.use('/files', require('./routes/files'));

app.get('/health', (req, res) => res.json({ ok: true }));

app.listen(3000);
