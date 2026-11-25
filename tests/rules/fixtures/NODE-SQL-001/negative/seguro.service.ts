import { Controller, Get, Query, Param, ParseIntPipe } from '@nestjs/common';
import { DataSource } from 'typeorm';

@Controller('clientes')
export class ClientesController {
  constructor(private readonly dataSource: DataSource) {}

  @Get()
  async buscar(@Query('nombre') nombre: string) {
    return this.dataSource.query('SELECT * FROM clientes WHERE nombre LIKE $1', [`%${nombre}%`]);
  }

  @Get(':id')
  async uno(@Param('id', ParseIntPipe) id: number) {
    return this.dataSource.query(`SELECT * FROM clientes WHERE id = ${id}`);
  }

  // Parámetro que no viene de la petición.
  async interno(tabla: string) {
    return this.dataSource.query(`SELECT COUNT(*) FROM ${tabla}`);
  }
}
