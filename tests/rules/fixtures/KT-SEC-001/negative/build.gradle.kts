import java.util.Properties

val secrets = Properties().apply {
    file("local.properties").inputStream().use { load(it) }
}

android {
    defaultConfig {
        buildConfigField("String", "MAPS_API_KEY", "\"${secrets["MAPS_API_KEY"]}\"")
        buildConfigField("String", "API_KEY_PLACEHOLDER", "\"your-api-key\"")
    }
}
