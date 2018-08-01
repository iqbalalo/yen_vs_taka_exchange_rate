## SET BACKEND
import matplotlib as mpl
mpl.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
import numpy as nm
import json


with open("remittance-rate.json") as f:
    data = json.load(f)

d = pd.DataFrame(data)
d['rate'] = d['rate'].astype('float64')
d['date'] = pd.to_datetime(d['date'], format="%Y-%m-%d")

d_month_mean = d.groupby(d['date'].dt.strftime("%Y-%m"))['rate'].mean().reset_index()
# reverse data frame for descending order
# d = d.iloc[::-1]
plt.plot(d_month_mean['date'], d_month_mean['rate'])
plt.ylim(0.6, 0.8)
plt.ylabel("average rate in taka per 1 yen")
plt.xlabel("year-month")
plt.xticks(rotation=90)
plt.grid(axis="both")
plt.suptitle("Average remittance rate of Yen vs BDT")
plt.title("based on 2 years data: (n = " + str(len(d)) + ") | n = days")
plt.gcf().subplots_adjust(bottom=0.2)
# plt.gcf().subplots_adjust(top=0.02)
# plt.tight_layout()
plt.show()
