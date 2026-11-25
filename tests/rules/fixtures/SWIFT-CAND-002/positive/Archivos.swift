import Foundation

func abrir(ruta: String, nombre: String) {
    let a = FileManager.default.contents(atPath: ruta)
    let b = URL(fileURLWithPath: ruta)
    try? FileManager.default.removeItem(atPath: ruta)
    let c = try? String(contentsOfFile: ruta, encoding: .utf8)
    let d = try? Data(contentsOf: b)
    let e = URL(fileURLWithPath: "/tmp/\(nombre)")
    _ = (a, c, d, e)
}
