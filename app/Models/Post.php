<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Post extends Model
{
    use HasFactory;

    protected $fillable = [
        'title', 'skills', 'year_exp', 'education', 'location', 'description'
    ];

    protected $casts = [
        'skills'   => 'array',   // <-- JSON ↔ Array auto
        'year_exp' => 'integer',
    ];
}