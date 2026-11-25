import Foundation

func abrir() {
    let a = FileManager.default.contents(atPath: "/etc/hosts")
    let b = URL(fileURLWithPath: "/tmp/cache.bin")
    try? FileManager.default.removeItem(atPath: "/tmp/cache.bin")
    let c = try? String(contentsOfFile: "datos.txt", encoding: .utf8)
    // let d = Data(contentsOf: otra)
    _ = (a, b, c)
}
