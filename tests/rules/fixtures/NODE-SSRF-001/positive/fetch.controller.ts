import { Controller, Get, Query } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';

@Controller('fetch')
export class FetchController {
  constructor(private readonly http: HttpService) {}

  @Get()
  async traer(@Query('url') url: string) {
    const { data } = await this.http.axiosRef.get(url);
    return data;
  }

  @Get('directo')
  async directo(@Query('url') url: string) {
    const r = await fetch(url);
    return r.text();
  }
}
