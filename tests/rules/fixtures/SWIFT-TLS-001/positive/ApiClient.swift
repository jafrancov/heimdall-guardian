import Alamofire
import Foundation

final class ApiClient: NSObject, URLSessionDelegate {
    private lazy var session: URLSession = {
        URLSession(configuration: .default, delegate: self, delegateQueue: nil)
    }()

    // Acepta cualquier certificado: un atacante en la red puede interceptar todo.
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        completionHandler(.useCredential, URLCredential(trust: challenge.protectionSpace.serverTrust!))
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        // Solo revisa el nombre del host, no la cadena.
        if challenge.protectionSpace.host.hasSuffix("miempresa.com"),
           let trust = challenge.protectionSpace.serverTrust {
            completionHandler(.useCredential, URLCredential(trust: trust))
            return
        }
        completionHandler(.performDefaultHandling, nil)
    }
}

enum Sessions {
    static let relaxed: Session = {
        let manager = ServerTrustManager(evaluators: [
            "api.miempresa.com": DisabledTrustEvaluator()
        ])
        return Session(serverTrustManager: manager)
    }()

    static let legacy = SessionManager(
        serverTrustPolicyManager: ServerTrustPolicyManager(policies: [
            "api.miempresa.com": .disableEvaluation
        ])
    )
}
