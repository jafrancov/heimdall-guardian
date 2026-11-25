import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:webview_flutter/webview_flutter.dart';

class PagoPage {
  late final WebViewController controller;

  void init(String url) {
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..addJavaScriptChannel(
        'Pago',
        onMessageReceived: (message) => procesarPago(message.message),
      )
      ..loadRequest(Uri.parse(url));
  }

  void registrar(InAppWebViewController c) {
    c.addJavaScriptHandler(handlerName: 'sesion', callback: (args) => token);
  }

  Widget legacy(String url) {
    return WebView(
      initialUrl: url,
      javascriptChannels: {
        JavascriptChannel(name: 'App', onMessageReceived: (m) {}),
      },
    );
  }
}
