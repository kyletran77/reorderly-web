from django.shortcuts import render

BASE = 'https://reorderly.com'


def content_index(request):
    articles = [
        {
            'title': 'How to Post on TikTok Every Day Without Burning Out',
            'slug': 'how-to-post-on-tiktok-every-day-without-burning-out',
            'description': 'The consistency trap is real. Here\'s why the algorithm punishes breaks, why batching only goes so far, and how automation is the only real solution.',
            'date': 'March 2026',
            'read_time': '7 min read',
            'tag': 'Strategy',
        },
        {
            'title': 'The Best AI Tools to Automate YouTube Shorts Creation in 2026',
            'slug': 'ai-tools-to-automate-youtube-shorts-2026',
            'description': 'Honest comparison of Opus Clip, Pictory, InVideo, and Descript — their real weaknesses, who they\'re actually for, and what to use if you have no footage.',
            'date': 'March 2026',
            'read_time': '8 min read',
            'tag': "Buyer's Guide",
        },
        {
            'title': 'How Long Does It Actually Take to Make a YouTube Short?',
            'slug': 'how-long-does-it-take-to-make-a-youtube-short',
            'description': 'A real time breakdown of every step: research, scripting, recording, editing, posting. The honest answer is over 2 hours per video.',
            'date': 'March 2026',
            'read_time': '5 min read',
            'tag': 'How-to Guide',
        },
        {
            'title': '5 Opus Clip Alternatives Worth Trying in 2026',
            'slug': 'opus-clip-alternatives-2026',
            'description': 'Why people leave Opus Clip (AI picks wrong moments, 2.4/5 on Trustpilot, scheduler breaks), and 4 real alternatives — plus one that doesn\'t need footage at all.',
            'date': 'March 2026',
            'read_time': '7 min read',
            'tag': "Buyer's Guide",
        },
        {
            'title': 'How to Grow on TikTok as a Small Business in 2026',
            'slug': 'how-to-grow-on-tiktok-as-a-small-business',
            'description': 'Consistency beats virality. What kinds of content work for SMBs, how to build a system, and how to post daily without it consuming your life.',
            'date': 'March 2026',
            'read_time': '8 min read',
            'tag': 'Growth Guide',
        },
    ]
    return render(request, 'content/index.html', {
        'title': 'Short-Form Video Guides — Karen',
        'description': 'Free guides on TikTok strategy, YouTube Shorts creation, AI video tools, and how to grow your business on short-form video without burning out.',
        'canonical': f'{BASE}/resources/',
        'articles': articles,
    })


def post_tiktok_daily(request):
    return render(request, 'content/post_tiktok_daily.html', {
        'title': 'How to Post on TikTok Every Day Without Burning Out — Karen',
        'description': 'The consistency trap is real. Here\'s why the algorithm punishes breaks, why batching only goes so far, and how automation is the only real solution.',
        'canonical': f'{BASE}/resources/how-to-post-on-tiktok-every-day-without-burning-out/',
    })


def ai_tools_youtube_shorts(request):
    return render(request, 'content/ai_tools_youtube_shorts.html', {
        'title': 'The Best AI Tools to Automate YouTube Shorts Creation in 2026 — Karen',
        'description': 'Honest comparison of Opus Clip, Pictory, InVideo, and Descript — their real weaknesses and what to use if you have no footage.',
        'canonical': f'{BASE}/resources/ai-tools-to-automate-youtube-shorts-2026/',
    })


def how_long_youtube_short(request):
    return render(request, 'content/how_long_youtube_short.html', {
        'title': 'How Long Does It Actually Take to Make a YouTube Short? — Karen',
        'description': 'A real time breakdown: research 30 min, scripting 20 min, recording 15 min, editing 45 min, posting 10 min. That\'s over 2 hours per Short.',
        'canonical': f'{BASE}/resources/how-long-does-it-take-to-make-a-youtube-short/',
    })


def opus_clip_alternatives(request):
    return render(request, 'content/opus_clip_alternatives.html', {
        'title': '5 Opus Clip Alternatives Worth Trying in 2026 — Karen',
        'description': 'Why people leave Opus Clip and 4 real alternatives — plus one that doesn\'t need footage at all.',
        'canonical': f'{BASE}/resources/opus-clip-alternatives-2026/',
    })


def grow_tiktok_small_business(request):
    return render(request, 'content/grow_tiktok_small_business.html', {
        'title': 'How to Grow on TikTok as a Small Business in 2026 — Karen',
        'description': 'Consistency beats virality. What kinds of content work for SMBs and how to post daily without it consuming your life.',
        'canonical': f'{BASE}/resources/how-to-grow-on-tiktok-as-a-small-business/',
    })
