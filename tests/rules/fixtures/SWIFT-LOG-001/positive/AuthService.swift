import Foundation
import os

final class AuthService {
    private let logger = Logger(subsystem: "com.miempresa.app", category: "auth")

    func login(user: String, password: String) async throws {
        print("Intentando login con password: \(password)")
        NSLog("token recibido: %@", accessToken)
        debugPrint("jwt=" + jwt)
        print(refreshToken)
        logger.info("sesión nueva \(sessionToken, privacy: .public)")
        os_log("clave de api %{public}@", apiKey)
        logger.debug("cvv de la tarjeta: \(card.cvv)")
    }
}
