from flask import Flask, request, jsonify
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASS = os.getenv("DB_PASS", "apppass")
DB_NAME = os.getenv("DB_NAME", "messages_db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "10"))
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


@app.get("/healthz")
def healthz():
try:
with get_conn() as _:
r.ping()
return {"status": "ok"}
except Exception as e:
return {"status": "error", "detail": str(e)}, 500


@app.get("/messages")
def list_messages():
cache_key = "messages:list"
cached = r.get(cache_key)
if cached:
return jsonify(json.loads(cached))


cn = get_conn()
cur = cn.cursor(dictionary=True)
cur.execute("SELECT id, author, body, created_at FROM messages ORDER BY id DESC LIMIT 100")
rows = cur.fetchall()
cur.close()
cn.close()


r.setex(cache_key, CACHE_TTL, json.dumps(rows))
return jsonify(rows)


@app.post("/messages")
def create_message():
data = request.get_json(force=True)
author = data.get("author", "anon")
body = data.get("body", "")
if not body:
return {"error": "body required"}, 400


# enqueue for the worker to process/normalize
payload = {"author": author, "body": body, "ts": datetime.utcnow().isoformat()}
r.lpush(QUEUE_KEY, json.dumps(payload))


# small UX trick: clear cache so GET shows fresh soon
r.delete("messages:list")
return {"status": "queued"}, 202


if __name__ == "__main__":
app.run(host="0.0.0.0", port=8080)