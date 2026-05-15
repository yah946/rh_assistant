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
        'skills'   => 'array', 
        'year_exp' => 'integer',
    ];
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    
    public function viewers(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'post_views')
                    ->withPivot('viewed_at')
                    ->withTimestamps();
    }
}