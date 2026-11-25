import Foundation

enum Endpoints {
    static let base = URL(string: "https://api.miempresa.com/v1")!

    #if DEBUG
    static let local = URL(string: "http://localhost:8080/v1")!
    static let loopback = URL(string: "http://127.0.0.1:8080/v1")!
    #endif

    // Antes usaba http://api.miempresa.com, ahora todo va por https.
    static let xmlns = "http://www.w3.org/2000/svg"

    func ping() {
        let request = URLRequest(url: URL(string: "https://status.miempresa.com/ping")!)
        URLSession.shared.dataTask(with: request).resume()
    }
}
