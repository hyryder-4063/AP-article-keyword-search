from nltk import data
import pandas as pd
from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray

students = {
    "Name": ["Asha", "Bharat", "Chirag", "Deepa", "Esha", "Farhan"],
    "Math": [80, 92, 75, 88, 90, 70],
    "Science": [85, 95, 78, 91, 87, 68],
    "English": [78, 88, 82, 90, 85, 72]
}

df = pd.DataFrame(students)

df["Total"] = df[["Math", "Science", "English"]].sum(axis=1)
df["Average"] = df[["Total"]]/3
high_achievers = df[df["Average"] >80]
print(high_achievers)


subject_averages = df[["Math", "Science", "English"]].mean()
print(subject_averages)

top_science = df.loc[df["Science"].idxmax()]
print(top_science["Name"], top_science["Science"])

df_sorted = df.sort_values(by=["Total"], ascending=False)
df_sorted.head(3)
print(df_sorted)



