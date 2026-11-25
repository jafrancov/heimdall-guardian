<?php
echo "Hola " . htmlspecialchars($_GET['nombre'], ENT_QUOTES, 'UTF-8');
$pagina = intval($_GET['pagina']);
echo $pagina;
echo "Bienvenido";

// A response declared as JSON is not rendered as HTML.
$result = save_record($_POST);
$json = json_encode($result);
header('Content-Type: application/json; charset=utf-8');
echo $json;

header("content-type: application/problem+json");
switch ($_GET['op']) {
    case 'list':
        echo json_encode(array('q' => $_GET['q']));
        break;
    default:
        echo $_GET['q'];
}
