import pandas as pd
import json
import matplotlib.pyplot as plt

with open('state_population_analysis.json') as f:
    data = json.load(f)

flat_data = []

for state, state_data in data.items():
    print(state)
    for time, time_data in state_data.items():
        flat_data.append(time_data | {"time": time, "state": state})

df = pd.DataFrame.from_dict(flat_data)


print(df.head())
print(df.columns)

df_30 = df[df["time"] == "30"][["population_percent", "state"]]

df_30.plot(x="state", y="population_percent", kind="bar")

df.set_index('state')

ax = df["population_percent"].plot.bar(x = "state", y = "population_percent", stacked=True)

plt.show()
