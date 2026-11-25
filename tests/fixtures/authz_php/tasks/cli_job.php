<?php
if (php_sapi_name() !== 'cli') {
    exit;
}
$m = new ReportModel();
$m->run();
file_put_contents('/tmp/report.txt', 'done');
