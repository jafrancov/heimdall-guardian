import 'package:webview_flutter/webview_flutter.dart';

class AvisoPage {
  late final WebViewController controller;

  void init() {
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.disabled)
      ..setNavigationDelegate(NavigationDelegate(
        onNavigationRequest: (request) => request.url.startsWith('https://www.ejemplo.mx')
            ? NavigationDecision.navigate
            : NavigationDecision.prevent,
      ))
      ..loadRequest(Uri.parse('https://www.ejemplo.mx/aviso'));
  }
}
