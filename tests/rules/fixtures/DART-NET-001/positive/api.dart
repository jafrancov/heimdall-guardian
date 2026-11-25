import 'package:dio/dio.dart';
import 'package:http/http.dart' as http;

const baseUrl = 'http://api.ejemplo.mx/v1';

class Api {
  final dio = Dio(BaseOptions(baseUrl: 'http://servicios.ejemplo.mx:8080', connectTimeout: const Duration(seconds: 5)));

  Future<http.Response> listar() {
    return http.get(Uri.parse('http://api.ejemplo.mx/v1/items'));
  }

  Future<http.Response> enviar(Map<String, String> datos) {
    return http.post(Uri.parse("http://192.168.1.50/api/enviar"), body: datos);
  }
}
