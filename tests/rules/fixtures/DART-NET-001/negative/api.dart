import 'package:dio/dio.dart';
import 'package:http/http.dart' as http;

const baseUrl = 'https://api.ejemplo.mx/v1';
const emulador = 'http://10.0.2.2:8000/api';
const local = 'http://localhost:3000';
const loopback = "http://127.0.0.1:5000/health";
const svgNs = 'http://www.w3.org/2000/svg';

class Api {
  final dio = Dio(BaseOptions(baseUrl: 'https://servicios.ejemplo.mx'));

  Future<http.Response> listar() {
    return http.get(Uri.parse('$baseUrl/items'));
  }
}
