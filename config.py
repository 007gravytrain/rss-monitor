# RSS Feed URLs to monitor
FEEDS = {
    "https://www.wsws.org/en/rss.xml": "World Socialist Web Site",
    "https://feed.dsausa.org/global/rss20.xml": "DSA - Global",
    "https://jacobin.com/feed/": "Jacobin",
    'https://prospect.org/api/rss/content.rss': "The American Prospect",
    "https://therealnews.com/feed?partner-feed=the-real-news-network": "The Real News Network",
    "https://www.socialistalternative.org/feed/": "Socialist Alternative",
    "https://www.leftvoice.org/feed": "Left Voice",
    "https://onlabor.org/feed/": "On Labor"
}

# Keywords to monitor (case insensitive)
KEYWORDS = ['Amazon', 'Whole Foods']

# How often to check feeds (in seconds)
CHECK_INTERVAL = 300  # 5 minutes, ignored in this setup since GitHub Actions controls timing

# Notification settings (uncomment and configure the one you want to use)
# Email Settings
EMAIL_SETTINGS = {
    'sender': 'xxxxxxxx@gmail.com',
    'password': 'xxxxxxx',  # Gmail requires an App Password
    'recipient': 'xxx@xxx.com',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 465
}
