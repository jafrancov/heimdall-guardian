const cp = require("child_process");
function ejecutar(cmd, archivo) {
  cp.exec(cmd);
  cp.execSync("convert " + archivo);
  cp.spawn(cmd, [], { shell: true });
}
