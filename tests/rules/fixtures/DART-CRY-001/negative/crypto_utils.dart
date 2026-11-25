import 'dart:convert';
import 'dart:math';

import 'package:crypto/crypto.dart';
import 'package:encrypt/encrypt.dart';

String checksum(List<int> fileBytes) {
  return md5.convert(fileBytes).toString();
}

String etag(String contenido) {
  return sha1.convert(utf8.encode(contenido)).toString();
}

String hmacSign(String message, String key) {
  return Hmac(sha256, utf8.encode(key)).convert(utf8.encode(message)).toString();
}

String generateToken() {
  final rnd = Random.secure();
  return List.generate(32, (_) => rnd.nextInt(256).toRadixString(16)).join();
}

int randomColorIndex() {
  return Random().nextInt(5);
}

String encryptGcm(String plain, Key key) {
  final iv = IV.fromSecureRandom(12);
  final encrypter = Encrypter(AES(key, mode: AESMode.gcm));
  return encrypter.encrypt(plain, iv: iv).base64;
}
