import 'package:sqflite/sqflite.dart';

Future<void> buscar(Database db, String nombre, String tabla, String sql) async {
  await db.rawQuery("SELECT * FROM users WHERE name = '$nombre'");
  await db.rawQuery('SELECT * FROM users WHERE name = \'${nombre.trim()}\'');
  await db.rawDelete('DELETE FROM users WHERE name = ' + nombre);
  await db.execute('DROP TABLE ' + tabla);
  await db.rawUpdate('UPDATE users SET a = 1 WHERE name = "$nombre"');
  await db.rawInsert(sql);
}
