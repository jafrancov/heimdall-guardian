import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';

@Module({
  imports: [
    JwtModule.register({
      global: true,
      secret: 'clave-de-desarrollo-123',
      signOptions: { expiresIn: '60s' },
    }),
  ],
})
export class AuthModule {}
