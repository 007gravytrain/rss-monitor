import feedparser
import datetime
import sqlite3
import time
import threading
import logging
import os
from datetime import datetime
from config import FEEDS, KEYWORDS  # Import only what's needed

class RSSMonitor:
    def __init__(self):
        print("Initializing RSS Monitor...")
        os.makedirs('data', exist_ok=True)
        
        self.conn = sqlite3.connect('data/rss_feeds.db', 
                                  check_same_thread=False,
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        sqlite3.register_adapter(datetime, lambda x: x.isoformat())
        sqlite3.register_converter('datetime', lambda x: datetime.fromisoformat(x.decode()))
        
        self.db_lock = threading.Lock()
        self.create_database()
        
        logging.basicConfig(
            filename='data/rss_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        print("Initialization complete.")

    def create_database(self):
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    link TEXT UNIQUE,
                    description TEXT,
                    published datetime,
                    feed_name TEXT,
                    keywords_matched TEXT,
                    processed_date datetime
                )
            ''')
            self.conn.commit()

    def check_feed(self, feed_url, feed_name):
        try:
            print(f"Checking feed: {feed_name}")
            feed = feedparser.parse(feed_url)
            new_articles = 0
            matched_articles = 0
            
            with self.db_lock:
                cursor = self.conn.cursor()
                
                for entry in feed.entries:
                    try:
                        pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    except:
                        pub_date = datetime.now()
                    
                    cursor.executcute('SELECT id FROM articles WHERE link = ?', (entry.link,))
                    if cursor.fetchone():
                        continue
                    
                    new_articles += 1
                    
                    content = f"{entry.title} {getattr(entry, 'description', '')}".lower()
                    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in content]
                    
                    if matched_keywords:
                        matched_articles += 1
                        print(f"Found matching article: {entry.title}")
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO articles 
                        (title, link, description, published, feed_name, keywords_matched, processed_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.title,
                        entry.link,
                        getattr(entry, 'description', ''),
                        pub_date,
                        feed_name,
                        ','.join(matched_keywords),
                        datetime.now()
                    ))
                
                self.conn.commit()
            
            print(f"Feed {feed_name} processed: {new_articles} new articles, {matched_articles} matches")
                
        except Exception as e:
            print(f"Error processing feed {feed_name}: {str(e)}")
            logging.error(f"Error processing feed {feed_name}: {str(e)}")

    def generate_html(self):
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM articles ORDER BY processed_date DESC LIMIT 50')
            articles = cursor.fetchall()
        
        html = """
        <html>
        <head>
            <title>RSS Monitor</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>RSS Feed Monitor</h1>
            <p>Monitoring feeds: {}</p>
            <p>Keywords: {}</p>
            <table>
                <tr>
                    <th>Title</th>
                    <th>Feed</th>
                    <th>Published</th>
                    <th>Keywords Matched</th>
                    <th>Processed</th>
                </tr>
        """.format(', '.join(FEEDS.values()), ', '.join(KEYWORDS))

        for article in articles:
            html += """
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            """.format(article[1], article[5], article[4], article[6], article[7])

        html += """
            </table>
        </body>
        </html>
        """
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html)

if __name__ == "__main__":
    monitor = RSSMonitor()
    for feed_url, feed_name in FEEDS.items():
        monitor.check_feed(feed_url, feed_name)
    monitor.generate_html()
    monitor.conn.close()
