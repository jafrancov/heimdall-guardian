import 'dart:convert';
import 'dart:math';

import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart';

String hashPassword(String password) {
  return md5.convert(utf8.encode(password)).toString();
}

String hashContrasena(String contrasena) {
  return sha1.convert(utf8.encode(contrasena)).toString();
}

String generateToken() {
  final rnd = Random();
  return List.generate(32, (_) => rnd.nextInt(256).toRadixString(16)).join();
}

String generateOtp() {
  final rnd = Random(DateTime.now().millisecondsSinceEpoch);
  return rnd.nextInt(999999).toString().padLeft(6, '0');
}

String encryptData(String plain, Key key) {
  final encrypter = Encrypter(AES(key, mode: AESMode.ecb));
  return encrypter.encrypt(plain).base64;
}

String encryptCbc(String plain, Key key) {
  final iv = IV.fromLength(16);
  return Encrypter(AES(key)).encrypt(plain, iv: iv).base64;
}

String encryptFixed(String plain, Key key) {
  final iv = IV.fromUtf8('0123456789abcdef');
  return Encrypter(AES(key)).encrypt(plain, iv: iv).base64;
}
