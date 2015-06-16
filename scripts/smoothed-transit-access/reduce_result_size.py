import pandas, numpy, sys, os
results = [f for f in os.listdir(os.getcwd()) if f.endswith('.csv')]

for f in results:
	df = pandas.read_csv(f)
	df = numpy.round(df)
	print f
	print df.head()
	if f.endswith('total.csv'):
		df.to_csv(f, columns=['ori','hi_access'])
	if f.endswith('minTT.csv'):
		df.to_csv(f, columns=['ori','lo_transittime'])