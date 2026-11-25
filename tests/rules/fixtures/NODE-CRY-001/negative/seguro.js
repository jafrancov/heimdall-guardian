const crypto = require('crypto');
const bcrypt = require('bcrypt');

async function hashContrasena(password) {
  return bcrypt.hash(password, 12);
}

// SHA-1 de un archivo, no de una contraseña (suma de verificación).
function sumaArchivo(contenido) {
  return crypto.createHash('sha1').update(contenido).digest('hex');
}

function nuevoToken() {
  return crypto.randomBytes(32).toString('hex');
}

// Math.random para algo que no es un secreto.
function colorAleatorio() {
  return Math.floor(Math.random() * 16777215).toString(16);
}

function barajar(lista) {
  return lista.sort(() => Math.random() - 0.5);
}

function cifrar(texto, clave) {
  const iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv('aes-256-gcm', clave, iv);
  return Buffer.concat([iv, c.update(texto, 'utf8'), c.final(), c.getAuthTag()]);
}
