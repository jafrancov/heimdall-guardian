import { Controller, Get, Query, Res } from '@nestjs/common';
import { Response } from 'express';

@Controller('mensajes')
export class MensajesController {
  @Get()
  mostrar(@Query('texto') texto: string, @Res() res: Response) {
    res.send(`<div class="aviso">${texto}</div>`);
  }
}
