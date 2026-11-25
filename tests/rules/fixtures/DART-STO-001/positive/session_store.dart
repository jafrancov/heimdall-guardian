import 'package:get_storage/get_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SessionStore {
  Future<void> saveLogin(String token, String refresh, String password) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    await prefs.setString(Keys.refreshToken, refresh);
    await prefs.setString('usuario_pwd', password);
    await prefs.setStringList('backup_codes_secret', ['1234', '5678']);
  }

  Future<void> saveValue(SharedPreferences prefs, String k, String accessToken) async {
    await prefs.setString(k, accessToken);
  }

  void cache(String jwt) {
    final box = GetStorage();
    box.write('jwt', jwt);
    GetStorage().write('session_id', '1');
  }
}

class Keys {
  static const refreshToken = 'refresh';
}
