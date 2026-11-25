const yaml = require('js-yaml');
const v8 = require('v8');

function cargar(req) {
  const a = JSON.parse(req.body.data);
  const b = yaml.load('clave: valor');
  const c = v8.deserialize("constante");
  const d = config.load(req.body.name);
  return [a, b, c, d];
}
