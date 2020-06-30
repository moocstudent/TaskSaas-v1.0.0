from django_redis import get_redis_connection

conn = get_redis_connection('default')
print(conn)
conn.set(123, 456, ex=10)
print(conn.get(123))
