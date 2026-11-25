import Foundation

enum Endpoints {
    static let base = URL(string: "http://api.miempresa.com/v1")!
    static let legacy = "http://pagos.miempresa.com/checkout"

    static func avatar(for id: String) -> URL? {
        URL(string: "http://cdn.miempresa.com/avatars/\(id).png")
    }

    func ping() {
        var request = URLRequest(url: URL(string: "http://status.miempresa.com/ping")!)
        request.httpMethod = "GET"
        URLSession.shared.dataTask(with: request).resume()
    }
}
