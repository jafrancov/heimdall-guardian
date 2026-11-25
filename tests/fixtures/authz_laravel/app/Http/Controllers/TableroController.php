<?php

class TableroController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth');
    }
}
