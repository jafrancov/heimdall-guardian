<?php
function ejecutar($archivo, $cmd)
{
    exec($cmd);
    shell_exec("convert " . $archivo . " salida.png");
    system($cmd, $codigo);
    $salida = `ls $archivo`;
}
