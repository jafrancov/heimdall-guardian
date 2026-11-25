import 'dart:io';

Future<void> abrir() async {
  await File('/tmp/cache.bin').readAsString();
  await Directory("/tmp/datos").list().toList();
  // await File(ruta).delete();
}
