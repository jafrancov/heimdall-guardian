const serialize = require('node-serialize');
const yaml = require('js-yaml');
const { unserialize } = require('node-serialize');

function leerPerfil(cookie) {
  const bruto = Buffer.from(cookie, 'base64').toString();
  return serialize.unserialize(bruto);
}

function leerOtro(texto) {
  return unserialize(texto);
}

function configuracion(texto) {
  return yaml.load(texto, { schema: yaml.DEFAULT_FULL_SCHEMA });
}

function viejo(respuesta) {
  return eval('(' + respuesta + ')');
}

module.exports = { leerPerfil, leerOtro, configuracion, viejo };
