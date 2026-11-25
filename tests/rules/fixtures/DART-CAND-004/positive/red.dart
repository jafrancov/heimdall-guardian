import 'package:http/http.dart' as http;
import 'package:webview_flutter/webview_flutter.dart';

Future<void> cargar(String destino, String id, WebViewController web, Uri uri) async {
  final a = Uri.parse(destino);
  await http.get(Uri.parse('https://api.example.com/items/$id'));
  await http.get(Uri.parse('https://api.example.com/' + id));
  await web.loadRequest(uri);
}
