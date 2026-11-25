import { Controller, Get, Query } from '@nestjs/common';
import * as fs from 'fs';
import { basename, join } from 'path';

@Controller('documentos')
export class DocumentosController {
  @Get()
  leer(@Query('nombre') nombre: string) {
    return fs.readFileSync(join(process.cwd(), 'docs', basename(nombre)), 'utf8');
  }

  guardar(nombre: string, datos: string) {
    fs.writeFileSync(join(process.cwd(), 'tmp', nombre), datos);
  }
}
