import * as crypto from 'crypto';
import * as CryptoJS from 'crypto-js';

export class CryptoService {
  firmar(password: string): string {
    return crypto.createHash('sha1').update(password).digest('hex');
  }

  generarCodigoReset() {
    const token = Math.floor(Math.random() * 1000000).toString();
    return { token };
  }

  cifrar(datos: string, clave: string) {
    return CryptoJS.AES.encrypt(datos, clave, { mode: CryptoJS.mode.ECB }).toString();
  }
}
