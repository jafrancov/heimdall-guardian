import 'dart:io';

import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/services.dart';

class ApiClient {
  late final Dio dio;

  ApiClient(Uint8List caBytes) {
    dio = Dio(BaseOptions(baseUrl: 'https://api.ejemplo.mx'));
    (dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final context = SecurityContext(withTrustedRoots: true)
        ..setTrustedCertificatesBytes(caBytes);
      return HttpClient(context: context);
    };
  }

  HttpClient pinned(String huellaEsperada) {
    final client = HttpClient();
    client.badCertificateCallback = (X509Certificate cert, String host, int port) {
      return cert.sha1.toString() == huellaEsperada && host == 'api.ejemplo.mx';
    };
    return client;
  }

  void rejects() {
    dio.httpClientAdapter = IOHttpClientAdapter(
      validateCertificate: (cert, host, port) => cert != null && host == 'api.ejemplo.mx',
    );
  }
}
