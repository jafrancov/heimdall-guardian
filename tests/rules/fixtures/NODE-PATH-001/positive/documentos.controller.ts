import { Controller, Get, Query, Res } from '@nestjs/common';
import { readFile } from 'fs/promises';
import * as fs from 'fs';
import { join } from 'path';

@Controller('documentos')
export class DocumentosController {
  @Get()
  async leer(@Query('nombre') nombre: string) {
    return fs.readFileSync(join(process.cwd(), 'docs', nombre), 'utf8');
  }
}
