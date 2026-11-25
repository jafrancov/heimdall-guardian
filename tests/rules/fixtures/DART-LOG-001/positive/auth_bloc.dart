import 'dart:developer' as developer;

import 'package:flutter/foundation.dart';
import 'package:logger/logger.dart';

class AuthBloc {
  final logger = Logger();

  Future<void> login(String user, String password) async {
    print('Intentando login con password: $password');
    final token = await api.login(user, password);
    debugPrint('Token recibido: ${session.accessToken}');
    logger.d('jwt: $token');
    logger.e(token);
    developer.log('card ' + cardNumber);
    print(token);
  }
}
