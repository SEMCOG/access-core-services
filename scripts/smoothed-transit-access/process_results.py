import pandas as pd, os, sys

# run this in the same folder as the results files generated with network_analyst.py
results = [x for x in os.listdir(os.getcwd()) if x.endswith(".csv")]
destination = results[0].split('_')[0]

minTT_df = pd.DataFrame()
total_df = pd.DataFrame()

for result in results:
    time = result.split('_')[-1].split('.')[0]
    df = pd.read_csv(result)

    # only need this if applying new cut-off
    # df = df[df['Total_Transit_TT'] <= 30]

    df['ori'],df['dest'] = zip(*df['Name'].apply(lambda x: x.split(' - ',1)))
    df.drop('Name', inplace=True, axis=1)
    total_series = df['ori'].value_counts()
    minTT_series = df.groupby(['ori'], sort=False)['Total_Transit_TT'].min()
    minTT_df['result_{0}'.format(time)] = minTT_series
    total_df['result_{0}'.format(time)] = total_series

total_df['hi_access'] = total_df[total_df.columns].max(axis=1)
minTT_df['lo_transittime'] = minTT_df[minTT_df.columns].min(axis=1)

total_df.to_csv('{0}_numberReachable.csv'.format(destination))
minTT_df.to_csv('{0}_minimumTravelTime.csv'.format(destination))
