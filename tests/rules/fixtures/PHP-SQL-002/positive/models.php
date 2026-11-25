<?php
class ModelReports {
    public function by_year($params) {
        $year = $params['year'];
        $month = $params['month'];
        $sql = "SELECT * FROM sales a WHERE year(a.created) = $year AND month(a.created) = " . $month;
        return $this->DB->query($sql);
    }

    public function by_name($name) {
        $sql = "SELECT * FROM users WHERE name = '$name'";
        return $this->db->query($sql);
    }

    public function filtered($f) {
        $sql = "SELECT * FROM items WHERE 1=1";
        if (!empty($f['kind'])) {
            $p = $f['kind'];
            $sql .= " AND kind = '$p'";
        }
        return $this->DB->query($sql);
    }
}

function find($id) {
    return mysqli_query($c, "SELECT * FROM t WHERE id=" . $id);
}

function legacy_lookup($conn, $code) {
    return sqlsrv_query($conn, "SELECT * FROM catalog WHERE code = '" . $code . "'");
}

class Repo {
    public function remove($ids) {
        $this->conn->exec("DELETE FROM t WHERE id IN (" . implode(",", $ids) . ")");
    }
}
