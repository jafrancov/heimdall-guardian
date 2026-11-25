import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:webview_flutter/webview_flutter.dart';

class AyudaPage {
  late final WebViewController controller;

  void init() {
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadRequest(Uri.parse('https://www.ejemplo.mx/ayuda'));
  }

  Widget legacy() {
    return WebView(
      initialUrl: 'https://www.ejemplo.mx/ayuda',
      javascriptMode: JavascriptMode.unrestricted,
    );
  }

  Widget inapp() {
    return InAppWebView(
      initialSettings: InAppWebViewSettings(javaScriptEnabled: true),
    );
  }
}
