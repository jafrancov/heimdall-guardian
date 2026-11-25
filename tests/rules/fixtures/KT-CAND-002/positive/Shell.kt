package app.util

class Shell {
    fun ejecutar(comando: String, archivo: String) {
        Runtime.getRuntime().exec(comando)
        Runtime.getRuntime().exec("ls " + archivo)
        Runtime.getRuntime().exec(arrayOf("cat", archivo))
        ProcessBuilder(comando, "-l").start()
        ProcessBuilder(listOf("sh", "-c", comando)).start()
    }
}
