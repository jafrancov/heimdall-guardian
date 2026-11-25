import { Controller, Get } from '@nestjs/common';
import { SkipAuth } from './auth/public.decorator';

@SkipAuth()
@Controller()
export class HealthController {
  @Get('health')
  health() {
    return 'ok';
  }
}
