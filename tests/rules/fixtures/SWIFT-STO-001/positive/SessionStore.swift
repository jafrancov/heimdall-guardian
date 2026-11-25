import Foundation
import SwiftUI

final class SessionStore {
    private let defaults = UserDefaults.standard

    func save(token: String, refreshToken: String) {
        defaults.set(token, forKey: "authToken")
        UserDefaults.standard.set(refreshToken, forKey: Keys.refresh)
    }

    func remember(userPassword: String) {
        UserDefaults.standard.set(userPassword, forKey: "last_login")
    }

    func savePin(_ pin: String) {
        defaults.setValue(pin, forKey: "user_pin")
    }
}

struct LoginView: View {
    @AppStorage("session_id") private var sessionId = ""
    @AppStorage("apiKey") var apiKey: String = ""

    var body: some View {
        VStack {
            Text("Hola")
            SecureField("Contraseña", text: $sessionId)
        }
    }
}
