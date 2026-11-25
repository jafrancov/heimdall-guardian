import 'package:sqflite/sqflite.dart';

class UserRepository {
  UserRepository(this.db);
  final Database db;

  Future<List<Map<String, Object?>>> buscar(String nombre) {
    return db.rawQuery("SELECT * FROM usuarios WHERE nombre = '$nombre'");
  }

  Future<List<Map<String, Object?>>> porId(String id) {
    return db.rawQuery('SELECT * FROM usuarios WHERE id = ' + id);
  }

  Future<int> borrar(String id) {
    return db.rawDelete('DELETE FROM usuarios WHERE id = ${id}');
  }

  Future<void> renombrar(String id, String nombre) async {
    await db.execute("UPDATE usuarios SET nombre = '" + nombre + "' WHERE id = ?", [id]);
  }

  Future<List<Map<String, Object?>>> filtrar(String estado) {
    return db.query('usuarios', where: "estado = '$estado'");
  }
}

class TareasDao {
  TareasDao(this.db);
  final AppDatabase db;

  Future<List<QueryRow>> buscar(String texto) {
    return db.customSelect("SELECT * FROM tareas WHERE titulo LIKE '%$texto%'").get();
  }
}
