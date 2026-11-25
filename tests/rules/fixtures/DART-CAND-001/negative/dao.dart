import 'package:sqflite/sqflite.dart';

Future<void> buscar(Database db, String nombre) async {
  await db.rawQuery('SELECT * FROM users WHERE name = ?', [nombre]);
  await db.rawDelete('DELETE FROM users WHERE id = ?', [1]);
  await db.execute('CREATE TABLE users (id INTEGER, name TEXT)');
  await db.rawInsert("INSERT INTO users (name) VALUES (?)", [nombre]);
  // await db.rawQuery('SELECT $nombre');
}
