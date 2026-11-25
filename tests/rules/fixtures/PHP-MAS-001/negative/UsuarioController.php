<?php
class UsuarioController
{
    public function store($request)
    {
        return Usuario::create($request->validated());
    }

    public function update($request, $usuario)
    {
        $usuario->update($request->only(['nombre', 'correo']));
    }
}

class Usuario extends Model
{
    protected $fillable = ['nombre', 'correo'];
    protected $guarded = ['id', 'rol'];
}
