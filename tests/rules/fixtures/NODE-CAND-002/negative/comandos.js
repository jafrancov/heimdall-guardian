const cp = require("child_process");
function ejecutar(archivo) {
  cp.exec("uptime");
  cp.execSync("df -h");
  cp.spawn("convert", [archivo]);
}
