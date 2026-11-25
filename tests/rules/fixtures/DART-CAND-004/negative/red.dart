import 'package:http/http.dart' as http;
import 'package:webview_flutter/webview_flutter.dart';

Future<void> cargar(WebViewController web) async {
  await http.get(Uri.parse('https://api.example.com/status'));
  await web.loadRequest(Uri.parse("https://app.example.com/ayuda"));
  // Uri.parse(destino);
}
