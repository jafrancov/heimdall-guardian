import Foundation
import Security

enum KeychainHelper {
    static func save(_ data: Data, account: String) -> OSStatus {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: account,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAlways
        ]
        SecItemDelete(query as CFDictionary)
        return SecItemAdd(query as CFDictionary, nil)
    }

    static func saveDevice(_ data: Data, account: String) -> OSStatus {
        var query = [String: Any]()
        query[kSecClass as String] = kSecClassGenericPassword
        query[kSecAttrAccount as String] = account
        query[kSecValueData as String] = data
        query[kSecAttrAccessible as String] = kSecAttrAccessibleAlwaysThisDeviceOnly
        return SecItemAdd(query as CFDictionary, nil)
    }
}

func configure() {
    let keychain = Keychain(service: "com.miempresa.app")
    keychain.accessibility(.always).set("valor", key: "k")
}
