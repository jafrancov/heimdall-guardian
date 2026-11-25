import Foundation
import WebKit

func cargar(destino: String, id: String, web: WKWebView, url: URL) {
    let a = URL(string: destino)
    let b = URL(string: "https://api.example.com/items/\(id)")
    let c = URL(string: "https://api.example.com/" + id)
    web.load(URLRequest(url: url))
    _ = (a, b, c)
}
