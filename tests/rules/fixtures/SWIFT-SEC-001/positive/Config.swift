import Foundation

enum AppConfig {
    static let apiKey = "@@FAKE_GOOGLE_KEY_B@@"
    static let clientSecret = "9f8e7d6c5b4a39281706f5e4d3c2b1a0"
    private let adminPassword = "Sup3rS3creta2024!"
}

struct PaymentClient {
    var token: String = "@@FAKE_STRIPE_KEY_B@@"
    let session = Session(apiKey: "d41d8cd98f00b204e9800998ecf8427e")
}
