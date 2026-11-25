import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'package:webview_flutter/webview_flutter.dart';

class TerminosPage {
  late final WebViewController controller;

  void init() {
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.disabled)
      ..loadRequest(Uri.parse('https://www.ejemplo.mx/terminos'));
  }

  Widget inapp() {
    return InAppWebView(
      initialSettings: InAppWebViewSettings(javaScriptEnabled: false),
    );
  }
}
