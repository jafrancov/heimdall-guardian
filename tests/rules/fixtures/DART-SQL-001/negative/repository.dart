import 'package:sqflite/sqflite.dart';

class UserRepository {
  UserRepository(this.db);
  final Database db;

  Future<List<Map<String, Object?>>> buscar(String nombre) {
    return db.rawQuery('SELECT * FROM usuarios WHERE nombre = ?', [nombre]);
  }

  Future<List<Map<String, Object?>>> activos() {
    return db.rawQuery('SELECT * FROM usuarios WHERE activo = 1');
  }

  Future<int> borrar(int id) {
    return db.delete('usuarios', where: 'id = ?', whereArgs: [id]);
  }

  Future<void> crear() async {
    await db.execute('CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nombre TEXT)');
    await db.execute('CREATE TABLE ' 'tareas (id INTEGER PRIMARY KEY)');
  }

  Future<List<Map<String, Object?>>> filtrar(String estado) {
    return db.query('usuarios', where: 'estado = ?', whereArgs: [estado]);
  }
}

class TareasDao {
  TareasDao(this.db);
  final AppDatabase db;

  Future<List<QueryRow>> buscar(String texto) {
    return db.customSelect(
      'SELECT * FROM tareas WHERE titulo LIKE ?',
      variables: [Variable.withString('%$texto%')],
    ).get();
  }
}
