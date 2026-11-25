import 'dart:io';

Future<void> abrir(String ruta, String nombre) async {
  await File(ruta).readAsString();
  await File('/tmp/$nombre').readAsString();
  await Directory(ruta).list().toList();
  var f = File(ruta + '.bak');
}
