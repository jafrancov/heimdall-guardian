<?php
// Function name straight from the query string.
$action = filter_input(INPUT_GET, 'action');
$params = filter_input_array(INPUT_GET);
$result = $action($params);
echo json_encode($result);

// Same through superglobals and the callable helpers.
function run_post() {
    $fn = $_POST['fn'];
    call_user_func($fn, 1);
    call_user_func_array($_REQUEST['cb'], array(1, 2));
}

// Class and method names chosen by the visitor.
function build() {
    $class = $_GET['type'];
    $obj = new $class();
    $method = $_GET['op'];
    $obj->$method();
    return $class::$method();
}

// function_exists() only says that the function exists, not that it is allowed.
function guarded_badly() {
    $name = $_REQUEST['name'];
    if (function_exists($name)) {
        return $name();
    }
}
