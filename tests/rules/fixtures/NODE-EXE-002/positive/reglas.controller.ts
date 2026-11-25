import { Body, Controller, Post } from '@nestjs/common';

@Controller('reglas')
export class ReglasController {
  @Post('evaluar')
  evaluar(@Body('condicion') condicion: string) {
    return eval(`(${condicion})`);
  }
}
