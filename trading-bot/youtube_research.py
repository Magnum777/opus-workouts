"""
youtube_research.py — YouTube Transcript Research Integration for TradeBot

Uses youtube-transcript-native-node skill to fetch video transcripts
for token/project research.

Usage:
    python youtube_research.py "Jupiter exchange review 2026"
    python youtube_research.py --symbol JUP --query "Jupiter exchange tutorial"

Returns: transcript text, metadata, video info for research context.
"""

import sys
import os
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

# Skill path
SKILL_DIR = Path(r'C:\Users\compj\.openclaw\workspace\skills\youtube-transcript-native-node')

def search_youtube_videos(query, max_results=5):
    """Search YouTube for videos matching query."""
    # Use web_search to find recent YouTube videos
    print(f"[YouTube] Searching for: {query}")
    
    search_query = f"{query} site:youtube.com"
    
    try:
        from web_search import web_search
        results = web_search(search_query, count=max_results)
        videos = []
        for r in results.get('results', []):
            url = r.get('url', '')
            if 'youtube.com/watch' in url or 'youtu.be/' in url:
                video_id = extract_video_id(url)
                if video_id:
                    videos.append({
                        'id': video_id,
                        'title': r.get('title', ''),
                        'url': url,
                        'snippet': r.get('snippet', '')
                    })
        return videos
    except Exception as e:
        print(f"[YouTube] Search error: {e}")
        return []

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript for a YouTube video using youtube-transcript-native-node."""
    try:
        # The skill uses Node.js — call it via subprocess
        skill_script = SKILL_DIR / 'youtube-transcript.js'
        if not skill_script.exists():
            # Try npm run or alternative entry points
            print(f"[YouTube] Skill script not found at {skill_script}")
            return None
        
        result = subprocess.run(
            ['node', str(skill_script), video_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {
                    'transcript': data.get('transcript', ''),
                    'language': data.get('language', ''),
                    'duration': data.get('duration', 0)
                }
            except json.JSONDecodeError:
                return {'transcript': result.stdout, 'language': 'unknown', 'duration': 0}
        else:
            print(f"[YouTube] Transcript error: {result.stderr[:200]}")
            return None
    except Exception as e:
        print(f"[YouTube] Error fetching transcript: {e}")
        return None

def analyze_video_content(transcript, token_symbol=None):
    """Extract relevant insights from transcript for TradeBot."""
    if not transcript:
        return None
    
    insights = {
        'mentions_token': False,
        'sentiment': 'neutral',
        'key_points': [],
        'technical_details': [],
        'partnerships': [],
        'tokenomics': []
    }
    
    text_lower = transcript.lower()
    
    # Check if token is mentioned
    if token_symbol and token_symbol.lower() in text_lower:
        insights['mentions_token'] = True
    
    # Extract sentiment indicators
    positive_words = ['bullish', 'growth', 'moon', 'adoption', 'partnership', 'launch', 'upgrade']
    negative_words = ['bearish', 'dump', 'rug', 'scam', 'delay', 'issue', 'problem']
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    if pos_count > neg_count + 2:
        insights['sentiment'] = 'positive'
    elif neg_count > pos_count + 2:
        insights['sentiment'] = 'negative'
    
    # Extract sentences with technical details
    tech_patterns = [
        r'tvl[\s\w]*(?:\$[\d,.]+[BMK]?|\d+\s*(?:million|billion))',
        r'(?:market cap|mcap)[\s\w]*(?:\$[\d,.]+[BMK]?|\d+\s*(?:million|billion))',
        r'(?:apy|apr)[\s\w]*\d+%?',
        r'(?:staking|yield|rewards?)\s+[\w\s]*\d+%?',
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text_lower)
        insights['technical_details'].extend(matches[:3])
    
    # Extract partnership mentions
    partnership_pattern = r'(?:partner|collaboration|integration|announce)[\w\s]*(?:with|from)\s+([A-Z][\w\s]{2,20})'
    partnerships = re.findall(partnership_pattern, transcript)
    insights['partnerships'] = list(set(partnerships))[:5]
    
    # Extract key points (sentences with numbers or percentages)
    sentences = re.split(r'[.!?]+', transcript)
    for sentence in sentences:
        if any(c in sentence for c in ['%', '$', 'million', 'billion']):
            if len(sentence) > 20 and len(sentence) < 200:
                insights['key_points'].append(sentence.strip())
    
    insights['key_points'] = insights['key_points'][:5]
    
    return insights

def research_token_via_youtube(symbol, query=None, max_videos=3):
    """Full pipeline: search → transcript → analyze for a token."""
    if not query:
        query = f"{symbol} token review analysis 2026"
    
    videos = search_youtube_videos(query, max_results=max_videos)
    
    if not videos:
        print(f"[YouTube] No videos found for {symbol}")
        return None
    
    results = []
    for video in videos:
        print(f"[YouTube] Processing: {video['title'][:60]}")
        
        transcript_data = get_transcript(video['id'])
        if transcript_data:
            insights = analyze_video_content(transcript_data['transcript'], symbol)
            results.append({
                'video': video,
                'transcript_length': len(transcript_data['transcript']),
                'language': transcript_data['language'],
                'insights': insights
            })
    
    return {
        'symbol': symbol,
        'query': query,
        'videos_found': len(videos),
        'videos_analyzed': len(results),
        'results': results
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='YouTube Research for TradeBot')
    parser.add_argument('query_or_symbol', help='Search query or token symbol')
    parser.add_argument('--symbol', '-s', help='Token symbol (if query is different)')
    parser.add_argument('--max-videos', '-n', type=int, default=3, help='Max videos to analyze')
    args = parser.parse_args()
    
    symbol = args.symbol or args.query_or_symbol
    query = args.query_or_symbol
    
    result = research_token_via_youtube(symbol, query, max_videos=args.max_videos)
    
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No results found")
        sys.exit(1)


if __name__ == '__main__':
    main()
