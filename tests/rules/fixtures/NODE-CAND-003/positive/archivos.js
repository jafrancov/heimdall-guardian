const fs = require("fs");
function servir(app, ruta, nombre) {
  fs.readFile(ruta, () => {});
  fs.createReadStream("/datos/" + nombre);
  app.get("/d", (req, res) => res.sendFile(ruta));
  app.get("/e", (req, res) => res.download(nombre));
}
