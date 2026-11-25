import UIKit
import WebKit

final class WebContainerViewController: UIViewController, WKScriptMessageHandler {
    private var webView: WKWebView!

    override func viewDidLoad() {
        super.viewDidLoad()
        let controller = WKUserContentController()
        controller.add(self, name: "nativeBridge")
        let config = WKWebViewConfiguration()
        config.userContentController = controller
        webView = WKWebView(frame: view.bounds, configuration: config)
        view.addSubview(webView)
        webView.load(URLRequest(url: URL(string: remoteUrl)!))
    }

    func registerPayments() {
        webView.configuration.userContentController.add(self, name: "payments")
        webView.configuration.userContentController.add(self, contentWorld: .page, name: "session")
        webView.configuration.userContentController.addScriptMessageHandler(self, contentWorld: .page, name: "legacy")
    }

    func userContentController(_ c: WKUserContentController, didReceive message: WKScriptMessage) {
        print(message.body)
    }
}
