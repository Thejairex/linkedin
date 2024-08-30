from db import Jobs

jobs = Jobs('jobs.db')

print(jobs.select_ids)
