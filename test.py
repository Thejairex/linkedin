from db import Jobs

jobs = Jobs('Data/jobs.db')

rows = jobs.select()
json =[dict(zip(jobs.columns, row)) for row in rows]
print(json)
