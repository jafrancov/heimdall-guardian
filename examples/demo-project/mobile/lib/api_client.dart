import 'dart:io';

import 'package:http/http.dart' as http;

const baseUrl = 'http://api.cornershop.example/v1';

class ApiClient {
  Future<http.Response> products() {
    return http.get(Uri.parse('http://api.cornershop.example/v1/products'));
  }

  HttpClient lenientClient() {
    final client = HttpClient();
    client.badCertificateCallback = (cert, host, port) => true;
    return client;
  }
}
