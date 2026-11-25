<?php
function ir()
{
    header("Location: /inicio");
    redirect("/inicio");
    return redirect()->to("/panel");
}
