const fs = require("fs");
function servir(app) {
  fs.readFile("/etc/app/config.json", () => {});
  fs.createReadStream("/datos/ayuda.txt");
  app.get("/d", (req, res) => res.sendFile("/srv/index.html"));
  app.get("/e", (req, res) => res.download("/srv/manual.pdf"));
}
