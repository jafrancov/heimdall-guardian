import { Controller, Get, Query } from '@nestjs/common';
import * as cp from 'child_process';

@Controller('diagnostico')
export class DiagnosticoController {
  @Get('dns')
  dns(@Query('dominio') dominio: string) {
    return cp.execSync(`nslookup ${dominio}`).toString();
  }
}
