import CommonCrypto
import CryptoKit
import CryptoSwift
import Foundation

enum CryptoHelper {
    static func hashPassword(_ password: String) -> String {
        let digest = Insecure.MD5.hash(data: Data(password.utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    static func legacyPasswordHash(_ pwd: String) -> String {
        let sha = Insecure.SHA1.hash(data: pwd.data(using: .utf8)!)
        return sha.description
    }

    static func checkPassword(_ input: String) -> [UInt8] {
        var digest = [UInt8](repeating: 0, count: Int(CC_MD5_DIGEST_LENGTH))
        CC_MD5(input, CC_LONG(input.utf8.count), &digest)
        return digest
    }

    static func encryptEcb(_ data: Data, key: Data) throws -> Data {
        var out = Data(count: data.count + kCCBlockSizeAES128)
        _ = CCCrypt(CCOperation(kCCEncrypt), CCAlgorithm(kCCAlgorithmAES), CCOptions(kCCOptionECBMode | kCCOptionPKCS7Padding), [UInt8](key), key.count, nil, [UInt8](data), data.count, &out, out.count, nil)
        return out
    }

    static func encryptFixedIv(_ message: String, key: [UInt8]) throws -> [UInt8] {
        let aes = try AES(key: key, blockMode: CBC(iv: "0123456789abcdef"), padding: .pkcs7)
        return try aes.encrypt(Array(message.utf8))
    }

    static func encryptZeroIv(_ message: String, key: [UInt8]) throws -> [UInt8] {
        let aes = try AES(key: key, blockMode: CBC(iv: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
        return try aes.encrypt(Array(message.utf8))
    }

    static func ecbMode(key: [UInt8]) throws -> AES {
        try AES(key: key, blockMode: ECB())
    }

    static func makeSessionToken() -> String {
        String(rand())
    }
}
