import Foundation
import WebKit

func cargar(web: WKWebView) {
    let a = URL(string: "https://api.example.com/status")
    web.load(URLRequest(url: URL(string: "https://app.example.com/ayuda")!))
    // let b = URL(string: destino)
    _ = a
}
