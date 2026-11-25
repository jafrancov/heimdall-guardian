import CommonCrypto
import CryptoKit
import CryptoSwift
import Foundation

enum CryptoHelper {
    static func fileChecksum(_ data: Data) -> String {
        // Suma de verificación de un archivo de caché, no protege nada.
        Insecure.MD5.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }

    static func cacheKey(_ url: String) -> [UInt8] {
        var digest = [UInt8](repeating: 0, count: Int(CC_SHA1_DIGEST_LENGTH))
        CC_SHA1(url, CC_LONG(url.utf8.count), &digest)
        return digest
    }

    static func hashPassword(_ password: String) -> String {
        SHA256.hash(data: Data(password.utf8)).description
    }

    static func encrypt(_ data: Data, key: SymmetricKey) throws -> Data {
        let sealed = try AES.GCM.seal(data, using: key)
        return sealed.combined!
    }

    static func encryptRandomIv(_ message: String, key: [UInt8]) throws -> [UInt8] {
        let iv = AES.randomIV(AES.blockSize)
        let aes = try AES(key: key, blockMode: CBC(iv: iv), padding: .pkcs7)
        return try aes.encrypt(Array(message.utf8))
    }

    static func makeSessionToken() -> String {
        var bytes = [UInt8](repeating: 0, count: 32)
        _ = SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
        return Data(bytes).base64EncodedString()
    }

    static func shuffleDemo() -> Int {
        Int(rand())
    }
}
