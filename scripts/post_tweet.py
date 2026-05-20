import tweepy
import json
import os
import random
import datetime

# API Credentials from GitHub Secrets
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(f"{datetime.datetime.utcnow().isoformat()} | {msg}")

def save_log():
    with open('tweet_log.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))

# Load tweets pool
try:
    with open('data/tweets.json', 'r', encoding='utf-8') as f:
        tweets_data = json.load(f)
    tweets = tweets_data.get('tweets', [])
    log(f"✅ Loaded {len(tweets)} tweets from pool")
except Exception as e:
    log(f"❌ Failed to load tweets.json: {e}")
    save_log()
    exit(1)

if not tweets:
    log("❌ No tweets in pool")
    save_log()
    exit(1)

# Validate credentials
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    log("❌ Missing Twitter API credentials. Check GitHub Secrets.")
    save_log()
    exit(1)

# Create Tweepy client
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Verify connection
try:
    me = client.get_me()
    if me.data:
        log(f"✅ Connected as @{me.data.username} (ID: {me.data.id})")
    else:
        log("⚠️ get_me returned no data, but no error")
except tweepy.errors.Unauthorized as e:
    log(f"❌ Unauthorized: Invalid API credentials. {e}")
    save_log()
    exit(1)
except Exception as e:
    log(f"⚠️ Could not verify user: {e}")

# Select a tweet (simple rotation: use random)
# Track posted tweets via a simple state file
state_file = 'tweet_state.json'
posted_ids = set()
try:
    with open(state_file, 'r') as f:
        state = json.load(f)
        posted_ids = set(state.get('posted', []))
except:
    pass

# Find unposted tweets
unposted = [t for t in tweets if t.get('id') not in posted_ids]
if not unposted:
    log("🔄 All tweets posted. Resetting rotation.")
    posted_ids = set()
    unposted = tweets[:]

# Select first unposted tweet (deterministic rotation)
tweet = unposted[0]
tweet_text = tweet.get('text', '')
tweet_id = tweet.get('id', 0)

log(f"📤 Posting tweet #{tweet_id}: {tweet_text[:60]}...")

# Post tweet
try:
    response = client.create_tweet(text=tweet_text)
    tweet_url = f"https://x.com/eerman883/status/{response.data['id']}"
    log(f"✅ Tweet posted! URL: {tweet_url}")
    
    # Update state
    posted_ids.add(tweet_id)
    with open(state_file, 'w') as f:
        json.dump({'posted': list(posted_ids), 'last_post': datetime.datetime.utcnow().isoformat()}, f)
        
except tweepy.errors.Forbidden as e:
    error_msg = str(e)
    if 'tier' in error_msg.lower() or 'write' in error_msg.lower() or 'access' in error_msg.lower():
        log(f"❌ TIER ERROR: Your API tier does not allow posting. Free tier is read-only. Upgrade to Basic ($200/mo) or Pay-Per-Use.")
    else:
        log(f"❌ Forbidden: {e}")
except tweepy.errors.TooManyRequests as e:
    log(f"⏳ Rate limit hit. Wait before retry. {e}")
except Exception as e:
    log(f"❌ Failed to post tweet: {e}")

save_log()
print("\n=== LOG ===")
print('\n'.join(log_lines))
