import Foundation
import os

final class AuthService {
    private let logger = Logger(subsystem: "com.miempresa.app", category: "auth")

    func login(user: String, password: String) async throws {
        print("Intentando login de \(user)")
        print("Longitud de la contraseña: \(password.count)")
        NSLog("token vacío: %d", token.isEmpty ? 1 : 0)
        logger.info("sesión nueva \(sessionToken, privacy: .private)")
        logger.info("sesión nueva \(sessionToken, privacy: .private(mask: .hash))")
        logger.debug("pasos completados: \(steps)")
        // print("password: \(password)")
        print("Mapa: \(mapPin)")
        print("Terminó el login")
    }
}
