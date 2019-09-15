from datetime import datetime
import pandas as pd

path = "../eatery-data/data.csv"
df = pd.read_csv(path)


def reformat_times(time):
    timestamp = datetime.strptime(time, "%I:%M %p")
    return timestamp.strftime("%H:%M")


df["start_time"] = df["start_time"].apply(reformat_times)
df["end_time"] = df["end_time"].apply(reformat_times)

df.to_csv(path, header=True, index=False)
