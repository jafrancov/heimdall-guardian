import UIKit
import WebKit

// Migrado desde UIWebView a WKWebView en la versión 3.0.
final class ModernBrowserViewController: UIViewController, WKNavigationDelegate {
    private let webView = WKWebView(frame: .zero)

    override func viewDidLoad() {
        super.viewDidLoad()
        webView.navigationDelegate = self
        webView.load(URLRequest(url: URL(string: "https://ayuda.miempresa.com")!))
    }
}
