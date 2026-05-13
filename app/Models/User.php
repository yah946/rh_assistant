<?php

namespace App\Models;
<<<<<<< HEAD
=======
use Tymon\JWTAuth\Contracts\JWTSubject;
>>>>>>> 6c34b9edf16158958147079c42c29f418b4c97d3

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use Database\Factories\UserFactory;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

#[Fillable(['name', 'email', 'password'])]
#[Hidden(['password', 'remember_token'])]
<<<<<<< HEAD
class User extends Authenticatable
=======
class User extends Authenticatable implements JWTSubject
>>>>>>> 6c34b9edf16158958147079c42c29f418b4c97d3
{
    /** @use HasFactory<UserFactory> */
    use HasFactory, Notifiable;

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
        ];
    }
<<<<<<< HEAD
=======
    public function getJWTIdentifier()
    {
        return $this->getKey();
    }
    public function getJWTCustomClaims()
    {
        return [
            'role' => $this->role
        ];
    }
>>>>>>> 6c34b9edf16158958147079c42c29f418b4c97d3
}
