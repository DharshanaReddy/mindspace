"""
Mood-based suggestion engine covering 8 emotional states with 100+ recommendations
across music, movies, and wellness activities.
"""

SUGGESTIONS: dict[str, dict[str, list[dict]]] = {
    "Happy": {
        "music": [
            {"title": "Happy", "artist": "Pharrell Williams", "vibe": "Pure joy"},
            {"title": "Can't Stop the Feeling", "artist": "Justin Timberlake", "vibe": "Danceable fun"},
            {"title": "Uptown Funk", "artist": "Bruno Mars & Mark Ronson", "vibe": "High energy"},
            {"title": "Good as Hell", "artist": "Lizzo", "vibe": "Self-love anthem"},
        ],
        "movies": [
            {"title": "Paddington 2", "year": 2017, "why": "Wholesome and genuinely delightful"},
            {"title": "Sing", "year": 2016, "why": "Colorful and uplifting musical"},
            {"title": "The Princess Bride", "year": 1987, "why": "Timeless feel-good adventure"},
        ],
        "wellness": [
            {"activity": "Dance like nobody's watching for 5 minutes", "type": "Movement"},
            {"activity": "Write down 3 things you're grateful for today", "type": "Mindfulness"},
            {"activity": "Call a friend you haven't spoken to in a while", "type": "Connection"},
            {"activity": "Try a new recipe and share it with someone", "type": "Creative"},
            {"activity": "Go for a walk without headphones and notice nature", "type": "Outdoor"},
        ],
    },
    "Sad": {
        "music": [
            {"title": "Fix You", "artist": "Coldplay", "vibe": "Gentle and healing"},
            {"title": "The Night We Met", "artist": "Lord Huron", "vibe": "Bittersweet nostalgia"},
            {"title": "Let Her Go", "artist": "Passenger", "vibe": "Reflective and honest"},
            {"title": "Someone Like You", "artist": "Adele", "vibe": "Emotional release"},
            {"title": "Holocene", "artist": "Bon Iver", "vibe": "Peaceful melancholy"},
        ],
        "movies": [
            {"title": "Inside Out", "year": 2015, "why": "Validates that sadness has value"},
            {"title": "Good Will Hunting", "year": 1997, "why": "Moving story of healing and growth"},
            {"title": "Little Miss Sunshine", "year": 2006, "why": "Finds beauty in imperfection"},
            {"title": "Soul", "year": 2020, "why": "Reminds you what makes life worth living"},
        ],
        "wellness": [
            {"activity": "Allow yourself to cry — it's a release, not weakness", "type": "Emotional"},
            {"activity": "Take a warm shower or bath", "type": "Self-Care"},
            {"activity": "Write in a journal about exactly how you feel", "type": "Mindfulness"},
            {"activity": "Reach out to one trusted person and say 'I'm not okay'", "type": "Connection"},
            {"activity": "Step outside for 10 minutes of fresh air", "type": "Outdoor"},
            {"activity": "Watch your favorite comfort show or movie", "type": "Rest"},
        ],
    },
    "Anxious": {
        "music": [
            {"title": "Weightless", "artist": "Marconi Union", "vibe": "Scientifically calming"},
            {"title": "Breathe (2 AM)", "artist": "Anna Nalick", "vibe": "Grounding and honest"},
            {"title": "Somewhere Over the Rainbow", "artist": "Israel Kamakawiwoole", "vibe": "Soothing hope"},
            {"title": "Clair de Lune", "artist": "Debussy", "vibe": "Classical calm"},
        ],
        "movies": [
            {"title": "The Secret Life of Walter Mitty", "year": 2013, "why": "Inspires courage over worry"},
            {"title": "Soul", "year": 2020, "why": "Shifts perspective on what matters"},
            {"title": "Wild", "year": 2014, "why": "Moving through fear one step at a time"},
        ],
        "wellness": [
            {"activity": "4-7-8 breathing: inhale 4s, hold 7s, exhale 8s — repeat 4 times", "type": "Breathing"},
            {"activity": "Ground yourself: name 5 things you see, 4 you touch, 3 you hear", "type": "Grounding"},
            {"activity": "Write your worries down, then close the notebook", "type": "Mindfulness"},
            {"activity": "Limit news and social media for the next 24 hours", "type": "Digital Detox"},
            {"activity": "Make a warm herbal tea (chamomile or lavender) and drink it slowly", "type": "Self-Care"},
            {"activity": "Take a 15-minute walk in nature without your phone", "type": "Outdoor"},
        ],
    },
    "Angry": {
        "music": [
            {"title": "Fighter", "artist": "Christina Aguilera", "vibe": "Channel frustration into strength"},
            {"title": "Roar", "artist": "Katy Perry", "vibe": "Empowering release"},
            {"title": "Stronger", "artist": "Kanye West", "vibe": "High-energy processing"},
            {"title": "Break Free", "artist": "Ariana Grande", "vibe": "Liberation and power"},
        ],
        "movies": [
            {"title": "Legally Blonde", "year": 2001, "why": "Turning anger into productive action"},
            {"title": "Rocky", "year": 1976, "why": "Channeling intensity into determination"},
            {"title": "Mad Max: Fury Road", "year": 2015, "why": "Cathartic high-energy release"},
        ],
        "wellness": [
            {"activity": "Do intense exercise — run, HIIT, or hit a punching bag", "type": "Movement"},
            {"activity": "Punch a pillow or squeeze a stress ball until you feel relief", "type": "Physical"},
            {"activity": "Write an angry letter you will NOT send — be completely honest", "type": "Journaling"},
            {"activity": "Take 10 slow deep breaths before saying or doing anything reactive", "type": "Breathing"},
            {"activity": "Splash cold water on your face and wrists", "type": "Physical"},
            {"activity": "Channel it: clean your space, reorganize, build something", "type": "Productive"},
        ],
    },
    "Lonely": {
        "music": [
            {"title": "Lean on Me", "artist": "Bill Withers", "vibe": "Reminder you're not alone"},
            {"title": "Count on Me", "artist": "Bruno Mars", "vibe": "Warm and reassuring"},
            {"title": "Bridge Over Troubled Water", "artist": "Simon & Garfunkel", "vibe": "Comforting and timeless"},
            {"title": "You've Got a Friend", "artist": "James Taylor", "vibe": "Pure comfort"},
            {"title": "With a Little Help from My Friends", "artist": "The Beatles", "vibe": "Community warmth"},
        ],
        "movies": [
            {"title": "The Intouchables", "year": 2011, "why": "An unlikely friendship that changes everything"},
            {"title": "Her", "year": 2013, "why": "Explores connection and loneliness with empathy"},
            {"title": "Cast Away", "year": 2000, "why": "Reminds you how resilient humans are"},
        ],
        "wellness": [
            {"activity": "Join an online community about something you love", "type": "Connection"},
            {"activity": "Volunteer at a local organization — giving fills the gap", "type": "Community"},
            {"activity": "Take yourself on a solo date: a movie, coffee shop, or bookstore", "type": "Self-Love"},
            {"activity": "Strike up a small conversation with someone nearby today", "type": "Social"},
            {"activity": "Tend to a plant or pet — nurturing builds connection", "type": "Nurturing"},
            {"activity": "Attend a local class, meetup, or event in person", "type": "Social"},
        ],
    },
    "Stressed": {
        "music": [
            {"title": "River Flows in You", "artist": "Yiruma", "vibe": "Peaceful piano"},
            {"title": "Moonlight Sonata", "artist": "Beethoven", "vibe": "Classical decompression"},
            {"title": "Weightless", "artist": "Marconi Union", "vibe": "Proven stress reducer"},
            {"title": "The Rain Song", "artist": "Led Zeppelin", "vibe": "Slow and grounding"},
        ],
        "movies": [
            {"title": "Chef", "year": 2014, "why": "Watching someone find joy in their craft is calming"},
            {"title": "Julie & Julia", "year": 2009, "why": "Cozy, focused, satisfying"},
            {"title": "The Secret Garden", "year": 2020, "why": "Visual and emotional relief"},
        ],
        "wellness": [
            {"activity": "Write a prioritized to-do list and tackle only the top 3 today", "type": "Organization"},
            {"activity": "Do a 10-minute body scan meditation (lie flat, breathe into each part)", "type": "Mindfulness"},
            {"activity": "Declutter one small area of your space for 15 minutes", "type": "Environment"},
            {"activity": "Turn off all notifications for the next hour", "type": "Digital Detox"},
            {"activity": "Take a 20-minute power nap — set an alarm", "type": "Rest"},
            {"activity": "Eat a real, nourishing meal away from your screen", "type": "Nourishment"},
            {"activity": "Progressive muscle relaxation: tense and release each muscle group", "type": "Body"},
        ],
    },
    "Hopeful": {
        "music": [
            {"title": "Eye of the Tiger", "artist": "Survivor", "vibe": "Pure motivation"},
            {"title": "Hall of Fame", "artist": "The Script ft. will.i.am", "vibe": "Dream-fueling anthem"},
            {"title": "Lose Yourself", "artist": "Eminem", "vibe": "Intense focus and drive"},
            {"title": "Shake It Out", "artist": "Florence + The Machine", "vibe": "Release and rise"},
        ],
        "movies": [
            {"title": "The Pursuit of Happyness", "year": 2006, "why": "Raw, inspiring perseverance"},
            {"title": "Hidden Figures", "year": 2016, "why": "Brilliance overcoming every obstacle"},
            {"title": "Billy Elliot", "year": 2000, "why": "Chasing a dream against all odds"},
        ],
        "wellness": [
            {"activity": "Set one specific, actionable goal with a deadline this week", "type": "Goal-Setting"},
            {"activity": "Create a simple vision board with images of what you're working toward", "type": "Visualization"},
            {"activity": "Read one chapter of an inspiring book or biography", "type": "Learning"},
            {"activity": "Work on your passion project for an uninterrupted 30 minutes", "type": "Creative"},
            {"activity": "Reach out to a mentor or someone you admire", "type": "Connection"},
            {"activity": "Write a letter to your future self about where you'll be in 1 year", "type": "Journaling"},
        ],
    },
    "Exhausted": {
        "music": [
            {"title": "Holocene", "artist": "Bon Iver", "vibe": "Soft and restorative"},
            {"title": "Breathe", "artist": "Pink Floyd", "vibe": "Permission to slow down"},
            {"title": "The Blower's Daughter", "artist": "Damien Rice", "vibe": "Quiet and gentle"},
            {"title": "Comptine d'un autre ete", "artist": "Yann Tiersen", "vibe": "Delicate and restful"},
        ],
        "movies": [
            {"title": "My Neighbor Totoro", "year": 1988, "why": "Soft, warm, no tension — pure rest"},
            {"title": "Amelie", "year": 2001, "why": "Gentle whimsy that asks nothing of you"},
            {"title": "The Grand Budapest Hotel", "year": 2014, "why": "Visually soothing and low-stakes"},
        ],
        "wellness": [
            {"activity": "Take a full rest day — cancel non-essential plans without guilt", "type": "Rest"},
            {"activity": "Do a digital detox for the entire evening", "type": "Digital Detox"},
            {"activity": "Take a warm bath with Epsom salts and dim lighting", "type": "Self-Care"},
            {"activity": "Gentle stretching or restorative yoga for 15 minutes", "type": "Movement"},
            {"activity": "Eat a simple, nourishing meal — don't skip food when tired", "type": "Nourishment"},
            {"activity": "Go to bed one hour earlier tonight — sleep is healing", "type": "Sleep"},
        ],
    },
    "Overwhelmed": {
        "music": [
            {"title": "The Sound of Silence", "artist": "Simon & Garfunkel", "vibe": "Stillness in the noise"},
            {"title": "Mad World", "artist": "Gary Jules", "vibe": "Quiet and real"},
            {"title": "Re: Stacks", "artist": "Bon Iver", "vibe": "Slow and undemanding"},
            {"title": "Saturn", "artist": "Stevie Wonder", "vibe": "Grounding and cosmic"},
        ],
        "movies": [
            {"title": "Lost in Translation", "year": 2003, "why": "No pressure — just being"},
            {"title": "Spirited Away", "year": 2001, "why": "Immersive world that quiets your own"},
            {"title": "About Time", "year": 2013, "why": "Slows you down and resets perspective"},
        ],
        "wellness": [
            {"activity": "Pick just ONE thing to do today and do only that", "type": "Focus"},
            {"activity": "Write a brain dump: everything on your mind, uncensored, for 5 minutes", "type": "Journaling"},
            {"activity": "Say no to one thing on your list — this week, not someday", "type": "Boundaries"},
            {"activity": "Sit outside without your phone for 10 minutes and do nothing", "type": "Rest"},
            {"activity": "Take 10 deep belly breaths, exhale twice as long as you inhale", "type": "Breathing"},
            {"activity": "Ask for help with one task — outsource or delegate something", "type": "Support"},
        ],
    },
    "Grateful": {
        "music": [
            {"title": "What a Wonderful World", "artist": "Louis Armstrong", "vibe": "Timeless warmth"},
            {"title": "Here Comes the Sun", "artist": "The Beatles", "vibe": "Gentle joy"},
            {"title": "Three Little Birds", "artist": "Bob Marley", "vibe": "Easy contentment"},
            {"title": "Beautiful Day", "artist": "U2", "vibe": "Open and expansive"},
        ],
        "movies": [
            {"title": "Chef", "year": 2014, "why": "Savoring life's simple pleasures"},
            {"title": "Coco", "year": 2017, "why": "Celebrating love, family, and memory"},
            {"title": "It's a Wonderful Life", "year": 1946, "why": "Timeless reminder of what matters"},
        ],
        "wellness": [
            {"activity": "Write a detailed thank-you letter to someone who shaped your life", "type": "Connection"},
            {"activity": "Take a photo walk — capture 10 things you find beautiful today", "type": "Mindfulness"},
            {"activity": "Share your gratitude with someone out loud — not just in your head", "type": "Social"},
            {"activity": "Savor your next meal: eat slowly, without screens, noticing each flavor", "type": "Mindfulness"},
            {"activity": "Reflect: write 3 ways your life is different (better) than 5 years ago", "type": "Journaling"},
            {"activity": "Pay it forward — do something kind for a stranger today", "type": "Community"},
        ],
    },
}

MOOD_EMOJIS: dict[str, str] = {
    "Happy": "😊",
    "Sad": "😢",
    "Anxious": "😰",
    "Angry": "😤",
    "Lonely": "🫂",
    "Stressed": "😩",
    "Hopeful": "🌟",
    "Exhausted": "😴",
    "Overwhelmed": "🌊",
    "Grateful": "🙏",
}


def get_suggestions(mood: str) -> dict:
    """Return all suggestions for a given mood, or a default if mood not found."""
    data = SUGGESTIONS.get(mood)
    if not data:
        # Fuzzy fallback: case-insensitive match
        for key in SUGGESTIONS:
            if key.lower() == mood.lower():
                data = SUGGESTIONS[key]
                mood = key
                break
    if not data:
        return {"error": f"Mood '{mood}' not recognized.", "available_moods": list(SUGGESTIONS.keys())}
    return {
        "mood": mood,
        "emoji": MOOD_EMOJIS.get(mood, ""),
        **data,
    }


def list_moods() -> list[dict]:
    return [{"mood": m, "emoji": e} for m, e in MOOD_EMOJIS.items()]
