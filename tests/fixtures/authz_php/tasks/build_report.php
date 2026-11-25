<?php
require_once __DIR__ . '/../models/report_model.php';
$m = new ReportModel();
$m->run();
file_put_contents('/tmp/report.txt', 'done');
