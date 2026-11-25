import 'package:encrypted_shared_preferences/encrypted_shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_storage/get_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SessionStore {
  final _secure = const FlutterSecureStorage();

  Future<void> saveLogin(String token, String refresh) async {
    await _secure.write(key: 'auth_token', value: token);
    await _secure.write(key: 'refresh_token', value: refresh);
  }

  Future<void> saveEncrypted(String token) async {
    final encryptedPrefs = EncryptedSharedPreferences();
    await encryptedPrefs.setString('auth_token', token);
  }

  Future<void> savePreferences(String idioma, bool oscuro) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('idioma', idioma);
    await prefs.setBool('modo_oscuro', oscuro);
    await prefs.setString('ultima_ciudad', 'Monterrey');
    GetStorage().write('onboarding_visto', true);
  }
}
