const serialize = require('node-serialize');
const yaml = require('js-yaml');
const v8 = require('v8');

function cargar(req, buf) {
  const a = serialize.unserialize(req.body.data);
  const b = yaml.load(req.body.config);
  const c = jsyaml.load(req.body.config);
  const d = v8.deserialize(buf);
  return [a, b, c, d];
}
