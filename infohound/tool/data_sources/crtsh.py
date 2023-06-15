import psycopg2

def get_subdomains(domain):
	subd = []
	try:
		conn = psycopg2.connect(
			host="crt.sh",
			database="certwatch",
			user="guest",
			port="5432"
		)
		conn.autocommit = True
		cur = conn.cursor()
		query = f"SELECT ci.NAME_VALUE NAME_VALUE FROM certificate_identity ci WHERE ci.NAME_TYPE = 'dNSName' AND reverse(lower(ci.NAME_VALUE)) LIKE reverse(lower('%.{domain}'))"
		cur.execute(query)
		result = cur.fetchall()
		cur.close()
		conn.close()
		for url in result:
			if "*" not in url[0]:
				subd.append(url[0])
	except Exception as e:
		print(e)
	return subd