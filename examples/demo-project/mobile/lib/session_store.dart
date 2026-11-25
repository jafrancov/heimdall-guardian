import 'package:shared_preferences/shared_preferences.dart';

class SessionStore {
  Future<void> saveLogin(String token, String refresh, String password) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    await prefs.setString('refresh_token', refresh);
    await prefs.setString('user_password', password);
  }
}
