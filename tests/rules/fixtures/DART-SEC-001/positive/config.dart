class AppConfig {
  static const String apiKey = 'k9Xp2LmQ7vTz4RbN8sWd';
  static const clientSecret = "s3cr3tDeProduccion2024";
  static final String _stripeSecretKey = 'sk_prod_4fG7hJ9kL2mN5pQ8';
  String adminPassword = 'Admin2024!mx';

  static const mapsApiKey = String.fromEnvironment('MAPS_KEY');

  FirebaseOptions options() {
    return FirebaseOptions(
      apiKey: 'AbCdEf0123456789xyz',
      appId: '1:123:android:abc',
    );
  }

  Future<void> boot() async {
    final authToken = 'eyJhbGciOiJIUzI1NiJ9.abc123';
    await login(user, 'x', accessToken: authToken);
  }
}
