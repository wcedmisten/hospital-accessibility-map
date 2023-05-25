import pandas as pd
import json
import matplotlib.pyplot as plt

with open("state_population_analysis.json") as f:
    data = json.load(f)

flat_data = []

for state, state_data in data.items():
    # print(state)
    for time, time_data in state_data.items():
        # fix rounding errors
        time_data["population_percent"] = min(100, time_data["population_percent"])
        time_data["area_percent"] = min(100, time_data["area_percent"])

        flat_data.append(
            time_data
            | {
                "time": time,
                "state": state.replace("District of Columbia", " Washington D.C."),
            }
        )

df = pd.DataFrame.from_dict(flat_data)

# pivot into a format usable for stacked bar graph
pivot = pd.pivot_table(
    data=df, index=["state"], columns=["time"], values="population_percent"
)

print(pivot)

# order by the 10 minute values
pivot = pivot.sort_values(by="40")

# use the diff between percents to stack up to 100%
pivot["40+"] = pivot.apply(lambda x: 100 - x["40"], axis=1)
pivot["40"] = pivot.apply(lambda x: max(0, x["40"] - x["30"]), axis=1)
pivot["30"] = pivot.apply(lambda x: max(0, x["30"] - x["20"]), axis=1)
pivot["20"] = pivot.apply(lambda x: max(0, x["20"] - x["10"]), axis=1)
pivot["10"] = pivot.apply(lambda x: x["10"], axis=1)

# use contract-boosted colors
pivot.plot.bar(
    stacked=True,
    color=["#cef062", "#7bc9c2", "#564a8a", "#db86db", "#ffffff"],
    edgecolor="black",
)

plt.xticks(rotation=45, ha="right")

plt.xlabel("State", fontsize=22)
plt.ylabel("% of State Population within X Minutes of a Hospital", fontsize=22)

handles, labels = plt.gca().get_legend_handles_labels()
order = [4, 3, 2, 1, 0]
plt.legend(
    [handles[idx] for idx in order],
    ["> 40", "30 - 40", "20 - 30", "10 - 20", "< 10"],
    fontsize=22,
    loc="lower right",
    title="Drive Time to Nearest Hospital (Mins)",
    title_fontsize=22,
)

plt.title("Comparison of Hospital Accessibility Across States", fontsize=30)

plt.tick_params(axis="both", which="major", labelsize=16)

plt.show()
