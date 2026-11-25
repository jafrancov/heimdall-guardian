import 'dart:io';

import 'package:dio/dio.dart';
import 'package:dio/io.dart';

class ApiClient {
  late final Dio dio;

  ApiClient() {
    dio = Dio(BaseOptions(baseUrl: 'https://api.ejemplo.mx'));

    // Para que funcione con el servidor de pruebas.
    (dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();
      client.badCertificateCallback = (X509Certificate cert, String host, int port) => true;
      return client;
    };
  }

  HttpClient legacyClient() {
    final client = HttpClient();
    client.badCertificateCallback = (cert, host, port) {
      print('Certificado aceptado para $host');
      return true;
    };
    return client;
  }

  void dio5() {
    dio.httpClientAdapter = IOHttpClientAdapter(
      validateCertificate: (cert, host, port) => true,
    );
  }

  Future<SecureSocket> socket(String host) {
    return SecureSocket.connect(host, 443, onBadCertificate: (X509Certificate c) => true);
  }
}
