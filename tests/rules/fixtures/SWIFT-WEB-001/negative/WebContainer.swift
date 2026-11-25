import UIKit
import WebKit

final class StaticPageViewController: UIViewController, WKNavigationDelegate {
    private var webView: WKWebView!
    private var items: [String] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        let config = WKWebViewConfiguration()
        config.preferences.javaScriptCanOpenWindowsAutomatically = false
        webView = WKWebView(frame: view.bounds, configuration: config)
        webView.navigationDelegate = self
        view.addSubview(webView)
        webView.load(URLRequest(url: URL(string: "https://ayuda.miempresa.com")!))
    }

    func collect() {
        items.append("uno")
        names.add(items, name: "lista")
    }

    func cleanup() {
        webView.configuration.userContentController.removeAllScriptMessageHandlers()
    }
}
