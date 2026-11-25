const yaml = require('js-yaml');

function leerPerfil(cookie) {
  return JSON.parse(Buffer.from(cookie, 'base64').toString());
}

function configuracion(texto) {
  return yaml.load(texto, { schema: yaml.JSON_SCHEMA });
}

function otra(texto) {
  return yaml.load(texto);
}

// Un método propio llamado unserialize dentro de una clase.
class Pila {
  unserialize(texto) {
    return JSON.parse(texto);
  }
}

// Browser helper in the style of php.js: a local function, no serialization package.
function unserialize(data) {
  return JSON.parse(data);
}
function leerValor(v) {
  return unserialize(atob(v));
}
