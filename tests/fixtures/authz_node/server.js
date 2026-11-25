const express = require('express');
const passport = require('passport');
const { ensureLoggedIn } = require('connect-ensure-login');
const { authenticate } = require('./middleware/auth');
const upload = require('./middleware/upload');
const usersRouter = require('./routes/users');
const reportsRouter = require('./routes/reports');
const publicRouter = require('./routes/public');
const adminRouter = require('./routes/admin');

const app = express();
app.use(express.json());

// Antes de authenticate global: sin protección.
app.get('/health', (req, res) => res.send('ok'));
app.post('/login', passport.authenticate('local'), (req, res) => res.redirect('/'));
app.post('/importar', upload.single('archivo'), importar);
app.get('/perfil', ensureLoggedIn(), perfil);
app.delete('/cuentas/:id', checkPermissions('admin'), borrarCuenta);

app.use('/api/users', usersRouter);
app.use('/api/reports', authenticate, reportsRouter);
app.use('/public', publicRouter);
app.use('/api/admin', adminRouter);

// A partir de aquí todo exige sesión.
app.use(authenticate);
app.get('/tarde', async function tablero(req, res) { res.json({}); });
app.put('/ajustes', asyncHandler(guardarAjustes));

function importar(req, res) { res.sendStatus(204); }

app.listen(3000);
