<?php
function listar($db, $mysqli, $nombre)
{
    mysqli_query($mysqli, "SELECT * FROM clientes");
    $stmt = $db->prepare("SELECT * FROM clientes WHERE nombre = ?");
    $stmt->execute([$nombre]);
    DB::select("SELECT * FROM clientes WHERE nombre = ?", [$nombre]);
    DB::raw("COUNT(*)");
}
