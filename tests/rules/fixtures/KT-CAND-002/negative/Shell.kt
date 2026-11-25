package app.util

class Shell {
    fun ejecutar() {
        Runtime.getRuntime().exec("uptime")
        Runtime.getRuntime().exec(arrayOf("ls", "-l"))
        ProcessBuilder("df", "-h").start()
        ProcessBuilder(listOf("uname", "-a")).start()
        // Runtime.getRuntime().exec(comando)
    }
}
