<?php
// Allowlist with early exit, as the entry point of a small JSON service.
$allowed = array('list_items', 'item_detail');
$action = filter_input(INPUT_GET, 'action');
$params = filter_input_array(INPUT_GET);
if (!is_string($action) || !in_array($action, $allowed, true)) {
    header('HTTP/1.1 400 Bad Request');
    exit;
}
echo json_encode($action($params));

// Allowlist in the positive branch.
function run_checked() {
    $fn = $_POST['fn'];
    if (in_array($fn, array('start', 'stop'))) {
        call_user_func($fn, 1);
    }
}

// Map of accepted values: the key is checked, the call uses a fixed name.
function dispatch_map() {
    $handlers = array('csv' => 'export_csv', 'pdf' => 'export_pdf');
    $kind = $_GET['kind'];
    if (!array_key_exists($kind, $handlers)) {
        return null;
    }
    $handler = $handlers[$kind];
    return $handler();
}

// Class chosen from a checked list.
function build() {
    $models = array('user', 'order');
    $type = $_GET['type'];
    if (!isset($models[$type])) {
        return null;
    }
    $class = 'Model_' . $models[$type];
    return new $class();
}

// Names that do not come from the request.
function internal($callback, $obj) {
    $fn = 'strtoupper';
    $method = 'save';
    $obj->$method();
    return $fn('a') . $callback('b');
}

// Literal dispatch on a switch.
function by_switch() {
    switch ($_GET['op']) {
        case 'a':
            return do_a();
        case 'b':
            return do_b();
    }
    return null;
}
