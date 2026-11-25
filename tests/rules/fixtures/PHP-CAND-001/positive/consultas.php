<?php
function listar($db, $mysqli, $tabla, $nombre)
{
    mysqli_query($mysqli, "SELECT * FROM " . $tabla);
    $db->query("SELECT * FROM clientes WHERE nombre = '$nombre'");
    DB::select("SELECT * FROM " . $tabla . " LIMIT 5");
    DB::raw("COUNT(" . $nombre . ")");
}
