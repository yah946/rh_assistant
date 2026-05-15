<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index()
    {
        $posts = Post::with(['user'])
            ->withCount([
                'viewers as total_views',
                'viewers as unique_viewers_count' => function($query) {
                    $query->distinct()->select('user_id');
                }
            ])
            ->latest()
            ->paginate(10);

        return response()->json([
            'success' => true,
            'data'    => $posts
        ]);
    }
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
        $post->load(['user', 'viewers']);

        $totalViews = $post->viewers()->count();
        $uniqueViewers = $post->viewers()->distinct()->count('user_id');

        return response()->json([
            'success' => true,
            'data'    => $post,
            'stats'   => [
                'total_views'   => $totalViews,
                'unique_viewers' => $uniqueViewers
            ]
        ]);
    }
    public function recordView(Post $post)
    {
        $post->viewers()->attach(auth()->id(), ['viewed_at' => now()]);
        return response()->json(['success' => true]);
    }
    public function stats(Post $post)
    {
        return response()->json([
            'success' => true,
            'post_id' => $post->id,
            'title' => $post->title,
            'total_views' => $post->viewers()->count(),
            'unique_viewers' => $post->viewers()->distinct()->count('user_id')
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
    public function destroy($id)
    {
        $post = Post::findOrFail($id);
        $post->delete();

        return response()->json([
            'success' => true,
            'message' => 'Post supprime avec succes'
        ]);
    }
}
