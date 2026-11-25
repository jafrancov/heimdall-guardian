import { Injectable } from '@nestjs/common';
import { Controller, Get, Query, Param } from '@nestjs/common';
import { DataSource } from 'typeorm';

@Controller('clientes')
export class ClientesController {
  constructor(private readonly dataSource: DataSource) {}

  @Get()
  async buscar(@Query('nombre') nombre: string) {
    return this.dataSource.query(`SELECT * FROM clientes WHERE nombre LIKE '%${nombre}%'`);
  }

  @Get(':id')
  async uno(@Param('id') id: string) {
    return this.dataSource.query('SELECT * FROM clientes WHERE id = ' + id);
  }
}
