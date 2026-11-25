import 'dart:io';

Future<void> ejecutar(String comando, List<String> args) async {
  await Process.run(comando, args);
  await Process.start(comando, ['-l']);
  Process.runSync('ls $comando', []);
}
