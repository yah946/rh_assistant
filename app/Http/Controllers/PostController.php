<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class PostController extends Controller
{
    public function store(Request $request)
    {
        $validated = $request->validate([
            'title'       => 'required|string|max:255',
            'skills'      => 'required|array|min:1',
            'skills.*'    => 'required|string|max:50',
            'year_exp'    => 'nullable|integer|min:0',
            'education'   => 'nullable|string|max:255',
            'location'    => 'nullable|string|max:255',
            'description' => 'required|string',
        ]);

        $post = Post::create($validated);
        return response()->json([
            'success' => true,
            'message' => 'Post cree avec succes',
            'data'    => $post
        ], 201);
    }

    public function show(Post $post)
    {
        return response()->json([
            'success' => true,
            'data'    => $post
        ]);
    }
    public function update(Request $request, $id)
    {
        $post = Post::findOrFail($id);
        $validated = $request->validate([
            'title'       => 'sometimes|required|string|max:255',
            'skills'      => 'sometimes|required|array|min:1',
            'skills.*'    => 'required|string|max:50',
            'year_exp'    => 'nullable|integer|min:0',
            'education'   => 'nullable|string|max:255',
            'location'    => 'nullable|string|max:255',
            'description' => 'sometimes|required|string',
        ]);

        $post->update($validated);
        
        return response()->json([
            'success' => true,
            'message' => 'Post mis a jour avec succes',
            'data'    => $post
        ], 200);
    }
}
