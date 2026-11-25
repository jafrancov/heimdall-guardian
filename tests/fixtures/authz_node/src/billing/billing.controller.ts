import { Controller, Get, Post, UseGuards } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { Public } from '../auth/public.decorator';
import { RolesGuard } from '../auth/roles.guard';

@Controller({ path: 'billing', version: '1' })
export class BillingController {
  @UseGuards(AuthGuard('jwt'), RolesGuard)
  @Post('charge')
  charge() {
    return {};
  }

  @Get('plans')
  plans() {
    return [];
  }

  @Public()
  @Get('webhook-status')
  status() {
    return 'ok';
  }
}
