import 'dart:io';

Future<void> ejecutar(List<String> args) async {
  await Process.run('uptime', []);
  await Process.start("df", ['-h']);
  // await Process.run(comando, args);
}
