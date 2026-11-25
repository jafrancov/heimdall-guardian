import Alamofire
import CryptoKit
import Foundation
import Security

final class SecureClient: NSObject, URLSessionDelegate {
    private let pinnedKeyHash = "q3wB6zGv0m7v0k1b2bY0JfN4gWk4d0hS4yq1x6mYb8c="

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let trust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        var error: CFError?
        guard SecTrustEvaluateWithError(trust, &error) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        completionHandler(.useCredential, URLCredential(trust: trust))
    }

    func pinned(
        _ session: URLSession,
        task: URLSessionTask,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let trust = challenge.protectionSpace.serverTrust,
              let key = SecTrustCopyKey(trust),
              let data = SecKeyCopyExternalRepresentation(key, nil) as Data?,
              Data(SHA256.hash(data: data)).base64EncodedString() == pinnedKeyHash else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        completionHandler(.useCredential, URLCredential(trust: trust))
    }

    func standard(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        completionHandler(.performDefaultHandling, nil)
    }
}

enum Sessions {
    static let strict: Session = {
        let manager = ServerTrustManager(evaluators: [
            "api.miempresa.com": PinnedCertificatesTrustEvaluator(),
            "cdn.miempresa.com": DefaultTrustEvaluator()
        ])
        return Session(serverTrustManager: manager)
    }()
}
