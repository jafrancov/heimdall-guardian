import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { JwtAuthGuard } from './auth/jwt-auth.guard';
import { HealthController } from './health.controller';
import { AuthController } from './auth/auth.controller';
import { CasesController } from './cases/cases.controller';
import { BillingController } from './billing/billing.controller';

@Module({
  controllers: [HealthController, AuthController, CasesController, BillingController],
  providers: [{ provide: APP_GUARD, useClass: JwtAuthGuard }],
})
export class AppModule {}
