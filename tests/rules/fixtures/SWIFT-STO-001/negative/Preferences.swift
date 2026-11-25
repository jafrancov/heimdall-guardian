import Foundation
import SwiftUI

final class Preferences {
    private let defaults = UserDefaults.standard

    func save(theme: String, hasSeenOnboarding: Bool, count: Int) {
        defaults.set(theme, forKey: "theme")
        defaults.set(hasSeenOnboarding, forKey: "hasSeenOnboarding")
        defaults.set(count, forKey: "launchCount")
        UserDefaults.standard.set(true, forKey: "tokenMigrationDone")
        UserDefaults.standard.set(Date(), forKey: "lastSync")
        defaults.set(false, forKey: "usesPinLock")
        defaults.set(passwordField.count, forKey: "passwordLength")
    }

    func storeSecret(_ token: String) throws {
        // Los datos sensibles van al Keychain.
        try Keychain.save(token, account: "authToken")
    }

    func shipping(_ mapping: String) {
        defaults.set(mapping, forKey: "shippingMapping")
    }
}

struct SettingsView: View {
    @AppStorage("dark_mode") private var darkMode = false
    @AppStorage("language") var language: String = "es"

    var body: some View {
        Toggle("Oscuro", isOn: $darkMode)
    }
}
