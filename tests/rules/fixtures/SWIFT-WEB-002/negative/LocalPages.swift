import WebKit

func makeWebView() -> WKWebView {
    let config = WKWebViewConfiguration()
    config.preferences.setValue(false, forKey: "allowFileAccessFromFileURLs")
    let view = WKWebView(frame: .zero, configuration: config)
    if let folder = Bundle.main.url(forResource: "help", withExtension: nil),
       let page = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "help") {
        view.loadFileURL(page, allowingReadAccessTo: folder)
    }
    return view
}
