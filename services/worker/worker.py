import os, time, json
import redis
import mysql.connector


DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "apppass")
DB_NAME = os.getenv("DB_NAME", "messages_db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
QUEUE_KEY = os.getenv("QUEUE_KEY", "events")


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_conn():
return mysql.connector.connect(
host=DB_HOST,
user=DB_USER,
password=DB_PASS,
database=DB_NAME,
autocommit=True,
)


print("worker starting...")
while True:
try:
item = r.brpop(QUEUE_KEY, timeout=5)
if not item:
continue
_, payload = item
data = json.loads(payload)
author = (data.get("author") or "anon").strip()[:80]
body = (data.get("body") or "").strip()[:1000]


# simple normalization: title case author
author = author.title() if author else "anon"


cn = get_conn()
cur = cn.cursor()
cur.execute("INSERT INTO messages(author, body) VALUES(%s,%s)", (author, body))
cur.close(); cn.close()
print("inserted message for", author)
except Exception as e:
print("worker error:", e)
time.sleep(1)