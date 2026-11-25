<?php
class UsuarioController
{
    public function store($request)
    {
        return Usuario::create($request->all());
    }

    public function update($request, $usuario)
    {
        $usuario->update($request->all());
    }
}

class Usuario extends Model
{
    protected $guarded = [];
}
