class AppConfig {
  static const String apiKey = String.fromEnvironment('API_KEY');
  static const String clientSecret = '';
  static const tokenKey = 'auth_token';
  static const passwordLabel = 'Contraseña';
  static const String apiKeyHeader = 'X-Api-Key';
  String password = 'cambia';
  String token = 'TU_TOKEN_AQUI';

  Widget buildField() {
    return TextField(
      decoration: InputDecoration(
        labelText: 'Contraseña del usuario',
        hintText: 'Escribe tu contraseña',
      ),
      obscureText: true,
    );
  }

  Map<String, String> headers(String token) => {
        'Authorization': 'Bearer $token',
        'apiKey': token,
      };

  void use(String secret) {
    final url = 'https://api.ejemplo.mx/v1';
    final tokenType = 'bearer-token-type';
    final passwordHint = 'Mínimo ocho caracteres';
  }
}
