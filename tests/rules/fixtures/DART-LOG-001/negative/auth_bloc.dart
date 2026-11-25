import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

class AuthBloc {
  final logger = Logger();

  Future<void> login(String user, String password) async {
    print('Intentando login de $user');
    final token = await api.login(user, password);
    debugPrint('Token recibido: longitud ${token.length}');
    logger.d('Sesión iniciada para ${session.userId}');
    logger.i('Refrescando token');
    print('Contraseña incorrecta');
    notifier.notify(token);
    analytics.log(token.length);
    print('Pinging server');
  }
}

class Antiguo {
  void login(String token) {
    // print(token);
    //   debugPrint('token: $token');
  }
}
