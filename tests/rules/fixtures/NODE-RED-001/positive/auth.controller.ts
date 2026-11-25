import { Controller, Get, Query, Res } from '@nestjs/common';
import { Response } from 'express';

@Controller('auth')
export class AuthController {
  @Get('callback')
  callback(@Query('state') state: string, @Res() res: Response) {
    return res.redirect(state);
  }
}
