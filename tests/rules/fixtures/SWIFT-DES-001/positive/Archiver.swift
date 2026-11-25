import Foundation

final class DraftStore {
    func load(from data: Data) -> Draft? {
        NSKeyedUnarchiver.unarchiveObject(with: data) as? Draft
    }

    func loadAll(from data: Data) -> Any? {
        try? NSKeyedUnarchiver.unarchiveTopLevelObjectWithData(data)
    }

    func open(_ data: Data) throws -> NSKeyedUnarchiver {
        let coder = try NSKeyedUnarchiver(forReadingFrom: data)
        coder.requiresSecureCoding = false
        return coder
    }
}
