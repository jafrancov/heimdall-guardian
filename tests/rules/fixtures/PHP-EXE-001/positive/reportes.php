<?php
$archivo = $_GET['archivo'];
system("cat /var/reportes/" . $archivo);
$salida = shell_exec("convert $archivo salida.pdf");
eval($codigo);
// One argument escaped, the other one not.
exec("cp " . escapeshellarg($origen) . " " . $destino);
system("tar -czf " . $nombre . ".tgz " . escapeshellarg($dir));
