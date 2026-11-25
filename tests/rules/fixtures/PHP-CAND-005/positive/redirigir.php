<?php
function ir($destino)
{
    header("Location: " . $destino);
    redirect($destino);
    return redirect()->to($destino);
}
