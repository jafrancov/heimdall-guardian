<?php
class ModelReportsSafe {
    public function by_year($params) {
        $year = (int) $params['year'];
        $sql = "SELECT * FROM sales a WHERE year(a.created) = $year";
        return $this->DB->query($sql);
    }

    public function by_id($id) {
        $sql = "SELECT * FROM t WHERE id = " . intval($id);
        return $this->DB->query($sql);
    }

    public function by_key($params) {
        $key = $this->DB->esc($params['key']);
        return $this->DB->query("SELECT * FROM t WHERE k = '$key'");
    }

    public function by_text($c, $text) {
        $t = mysqli_real_escape_string($c, $text);
        return mysqli_query($c, "SELECT * FROM t WHERE x = '$t'");
    }

    public function prepared($c, $name) {
        $stmt = $c->prepare("SELECT * FROM t WHERE name = ?");
        $stmt->bind_param("s", $name);
        $stmt->execute();
        return $stmt->get_result();
    }

    public function unused($label) {
        $this->log($label);
        return $this->DB->query("SELECT * FROM t");
    }

    public function constant() {
        return $this->DB->query("SELECT COUNT(*) FROM t WHERE active = 1");
    }

    public function page($n) {
        $limit = (int) $n;
        return $this->DB->query("SELECT * FROM t LIMIT " . $limit);
    }
}

function from_request() {
    // Request superglobals are PHP-SQL-001's business, not a parameter.
    return mysqli_query($GLOBALS['c'], "SELECT * FROM t WHERE id = " . $_GET['id']);
}

function escaped_with_helper($conn, $value) {
    $safe = db_escape($conn, $value);
    return mysqli_query($conn, "SELECT * FROM t WHERE v = '$safe'");
}

class Folios {
    public function duplicated($year, $ids) {
        $ids = array_map('intval', (array) $ids);
        $list = implode(',', $ids);
        return $this->DB->query("SELECT * FROM t WHERE folio IN ($list)");
    }
}
