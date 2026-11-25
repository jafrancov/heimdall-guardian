const libxmljs = require('libxmljs');
const xml2js = require('xml2js');
const { DOMParser } = require('@xmldom/xmldom');

function leer(req) {
  const a = libxmljs.parseXml('<a><b/></a>');
  const c = new DOMParser().parseFromString('<a/>', 'text/xml');
  xml2js.parseString("<root/>", (err, res) => res);
  const d = JSON.parse(req.body.json);
  const e = route.parseFromString(req.body.xml);
}
