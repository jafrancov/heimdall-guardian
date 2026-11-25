import UIKit

final class LegacyBrowserViewController: UIViewController, UIWebViewDelegate {
    @IBOutlet private var browser: UIWebView!

    override func viewDidLoad() {
        super.viewDidLoad()
        browser.delegate = self
        browser.loadRequest(URLRequest(url: URL(string: "https://ayuda.miempresa.com")!))
    }

    func makeInline() -> UIWebView {
        let view = UIWebView(frame: .zero)
        return view
    }
}
