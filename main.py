from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import fastf1

# Load session, filter out inlaps, outlaps, and restrict to green flag laps
session = fastf1.get_session(2025, 'Belgium', 'R')
session.load(laps=True)
race_laps = (session.laps
                .pick_track_status("1")
                .loc[lambda df: df["PitInTime"].isna() & df["PitOutTime"].isna()])

# convert to a data frame compatible with Isolation Forest
df = (race_laps
    .assign(LapTime_s = race_laps["LapTime"].dt.total_seconds())
    .loc[:, ["LapNumber", "LapTime_s"]]
    .dropna())
df = df[df["LapNumber"] > 2]

# Plot data on scatter graph
plt.scatter(
    df["LapNumber"],
    df["LapTime_s"],
    s=15
)
plt.xlabel("Lap number")
plt.ylabel("Lap time [s]")
plt.title("All drivers – 2021 Silverstone GP")
plt.show()

# Scale so lap number doesnt dominate anomalies
X = StandardScaler().fit_transform(df)

# Fit model and add a boolean column which defines whether a lap is an anomaly
iso = IsolationForest(contamination=0.045, random_state=42).fit(X)
df["anomaly"] = iso.predict(X) == -1

# Normal laps
plt.scatter(
    df.loc[~df["anomaly"], "LapNumber"],
    df.loc[~df["anomaly"], "LapTime_s"],
    c="blue", s=15, label="Normal"
)

# Anomalous laps
plt.scatter(
    df.loc[df["anomaly"], "LapNumber"],
    df.loc[df["anomaly"], "LapTime_s"],
    c="red", s=15, label="Anomaly"
)

plt.xlabel("Lap number")
plt.ylabel("Lap time [s]")
plt.title("Lap-time anomalies")
plt.legend()
plt.tight_layout()
plt.show()