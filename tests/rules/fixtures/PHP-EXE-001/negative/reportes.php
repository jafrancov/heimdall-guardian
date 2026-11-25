<?php
system("date");
$salida = shell_exec("uptime");
exec("ls " . __DIR__, $lineas);
system(escapeshellcmd($comando));
// Every variable goes through the escaping functions.
exec("chown -R www-data " . escapeshellarg($ruta));
system("convert " . escapeshellarg($origen) . " " . escapeshellarg(basename($destino)) . " 2>&1");
$salida = shell_exec('ls -l ' . escapeshellarg($dir . '/datos'));
