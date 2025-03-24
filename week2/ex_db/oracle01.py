import cx_Oracle

conn = cx_Oracle.connect("member", "member", "localhost:1521/xe")
print(conn.version)
sql ="""
    SELECT *
    FROM member
    WHERE mem_name LIKE '%' || :1 || '%'
"""
cur = conn.cursor()
rows = cur.execute(sql, ['은'])
for row in rows:
    print(row)
conn.close()