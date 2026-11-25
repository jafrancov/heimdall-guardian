import { Body, Controller, Post } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';

@Controller('cuentas')
export class CuentasController {
  constructor(@InjectModel('Cuenta') private readonly cuentas: Model<any>) {}

  @Post('entrar')
  async entrar(@Body() credenciales: any) {
    return this.cuentas.findOne(credenciales);
  }

  @Post('baja')
  async baja(@Body('correo') correo: string) {
    return this.cuentas.updateOne({ correo }, { activa: false });
  }
}
