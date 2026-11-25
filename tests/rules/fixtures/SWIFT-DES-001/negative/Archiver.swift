import Foundation

final class DraftStore {
    func load(from data: Data) -> Draft? {
        try? NSKeyedUnarchiver.unarchivedObject(ofClass: Draft.self, from: data)
    }

    func open(_ data: Data) throws -> NSKeyedUnarchiver {
        let coder = try NSKeyedUnarchiver(forReadingFrom: data)
        coder.requiresSecureCoding = true
        return coder
    }

    func decode(_ data: Data) throws -> Draft {
        try JSONDecoder().decode(Draft.self, from: data)
    }
}
