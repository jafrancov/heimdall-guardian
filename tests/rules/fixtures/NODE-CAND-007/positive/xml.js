const libxmljs = require('libxmljs');
const xml2js = require('xml2js');
const { DOMParser } = require('@xmldom/xmldom');

function leer(req) {
  const a = libxmljs.parseXml(req.body.xml, { noent: true });
  const b = libxmljs.parseXmlString(req.body.xml);
  const c = new DOMParser().parseFromString(req.body.xml, 'text/xml');
  xml2js.parseString(req.body.xml, (err, res) => res);
  const parser = new DOMParser();
  const d = parser.parseFromString(req.body.xml, 'text/xml');
}
