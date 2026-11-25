<?php
function ejecutar()
{
    exec("uptime");
    shell_exec("df -h");
    system("ls -l", $codigo);
}
