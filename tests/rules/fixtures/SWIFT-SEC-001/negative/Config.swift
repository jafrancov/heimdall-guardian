import Foundation

enum AppConfig {
    static let apiKey = Bundle.main.object(forInfoDictionaryKey: "API_KEY") as? String ?? ""
    static let tokenKey = "com.miempresa.app.authToken"
    static let passwordKeychainAccount = "com.miempresa.app.password"
    static let passwordPlaceholder = "Ingresa tu contraseña"
    static let apiKeyHeader = "X-Api-Key"
    static let clientSecret = ProcessInfo.processInfo.environment["CLIENT_SECRET"] ?? ""
    static let tokenType = "Bearer"
    static let secretPlaceholder = "your-secret-here"
    // static let apiKey = "@@FAKE_GOOGLE_KEY_B@@"
    static let exampleToken = "change_me_token_value"
    static let userDefaultsToken = "AUTH_TOKEN_KEY"
    static let shortPassword = "abc"
}

struct Strings {
    let passwordLabel = "Contraseña de la cuenta"
    let tokenError = "El token expiró, inicia sesión otra vez"
}
