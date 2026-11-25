import WebKit

func makeWebView() -> WKWebView {
    let config = WKWebViewConfiguration()
    config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
    config.setValue(true, forKey: "allowUniversalAccessFromFileURLs")
    let view = WKWebView(frame: .zero, configuration: config)
    return view
}

func makeLegacyWebView() -> WKWebView {
    let prefs = WKPreferences()
    prefs.setValue(1, forKey: "allowFileAccessFromFileURLs")
    prefs.setValue(1, forKey: "allowUniversalAccessFromFileURLs")
    let config = WKWebViewConfiguration()
    config.preferences = prefs
    return WKWebView(frame: .zero, configuration: config)
}
