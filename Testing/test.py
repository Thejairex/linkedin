import pandas as pd

from db import Jobs

jobs = Jobs('test.db')

jobs.insert(1, 'title', 'company', 'location', True, 'keywosrd', 'link')
print(jobs.columns)
df = pd.DataFrame(jobs.select(), columns=jobs.columns)
print(df.head())