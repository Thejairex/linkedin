from urllib.parse import urlparse, parse_qs

# Supongamos que obtienes la URL actual del driver
current_url = "https://www.linkedin.com/jobs/search/?currentJobId=3948747335&keywords=Data%20Scientist&origin=SWITCH_SEARCH_VERTICAL"

# Analizar la URL
parsed_url = urlparse(current_url)

# Extraer los parámetros de la query string
query_params = parse_qs(parsed_url.query)

# Acceder a un parámetro específico, por ejemplo "id"
id_param = query_params.get('currentJobId', [None])[0]  # [None] es el valor predeterminado si no se encuentra el parámetro

# Imprimir el valor del parámetro
print(f"El valor del parámetro 'id' es: {id_param}")
