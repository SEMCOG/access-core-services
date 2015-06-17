working_gdb_path = 'C:/Users/mcbroom/Desktop/access.gdb'

def network_analysis(gdb_path=working_gdb_path,
					destination='destination_grocery_super',
					destination_field='Establishm',
					origin='origin_naTransitCentroids',
					origin_field='node_id',
					mode='transit',
					cutoff=30,
					start='8:00:00',
					ampm='AM',
					date='6/1/2015',
					step_amount=1,
					minutes_to_step=30):
	import arcpy

	# check for na extension
	if arcpy.CheckExtension("Network") == "Available":
		arcpy.CheckOutExtension("Network")
		print "checked out Network Analyst license..."
	else:
		return "Network Analyst license is unavailable, ask Ann ^_^"

	# create list of times

	start_times=[ '{0}{1}'.format(start[:-5], str(x).zfill(2)) for x in xrange(minutes_to_step)]

	for time in start_times:
		time_to_eval = '{0} {1}{2} {3}'.format(date,time,start[-3:],ampm)
		print "Evaluating {0}".format(time_to_eval)
		print "Creating OD Cost Matrix Layer..."

		outNALayer = arcpy.MakeODCostMatrixLayer_na(
			in_network_dataset="{0}/semTransit/semTransit_ND".format(gdb_path),
            out_network_analysis_layer="OD Cost Matrix",
            impedance_attribute="Transit_TT",
            default_cutoff="{0}".format(cutoff),
            default_number_destinations_to_find="#",
            accumulate_attribute_name="#",
            UTurn_policy="ALLOW_UTURNS",
            restriction_attribute_name="#",
            hierarchy="NO_HIERARCHY",
            hierarchy_settings="#",
            output_path_shape="NO_LINES",
            time_of_day=time_to_eval)

		outNALayer = outNALayer.getOutput(0)
		subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
		originsLayerName = subLayerNames["Origins"]
		destinationsLayerName = subLayerNames["Destinations"]
		linesLayerName = subLayerNames["ODLines"]

		print "Adding Destinations"
		arcpy.AddLocations_na(
			in_network_analysis_layer="OD Cost Matrix",
            sub_layer="Destinations",
            in_table=destination,
            field_mappings="Name {0} #".format(destination_field),
            search_tolerance="5000 Meters",
            sort_field="#",
            search_criteria="Connectors_Stops2Streets NONE;Streets_UseThisOne SHAPE;TransitLines NONE;Stops NONE;Stops_Snapped2Streets NONE;semTransit_ND_Junctions NONE",
            match_type="MATCH_TO_CLOSEST",
            append="APPEND",
            snap_to_position_along_network="NO_SNAP",
            snap_offset="5 Meters",
            exclude_restricted_elements="INCLUDE",
            search_query="Connectors_Stops2Streets #;Streets_UseThisOne #;TransitLines #;Stops #;Stops_Snapped2Streets #;semTransit_ND_Junctions #")

		print "Adding origins"
		arcpy.AddLocations_na(
			in_network_analysis_layer="OD Cost Matrix",
			sub_layer="Origins",
			in_table=origin,
			field_mappings="Name {0} #".format(origin_field),
			search_tolerance="5000 Meters",
			sort_field="#",
			search_criteria="Connectors_Stops2Streets NONE;Streets_UseThisOne SHAPE;TransitLines NONE;Stops NONE;Stops_Snapped2Streets NONE;semTransit_ND_Junctions NONE",
			match_type="MATCH_TO_CLOSEST",
			append="APPEND",
			snap_to_position_along_network="NO_SNAP",
			snap_offset="5 Meters",
			exclude_restricted_elements="INCLUDE",
			search_query="Connectors_Stops2Streets #;Streets_UseThisOne #;TransitLines #;Stops #;Stops_Snapped2Streets #;semTransit_ND_Junctions #")

		print "Begin Solving"
		arcpy.na.Solve(outNALayer)

		outFile = '/'.join(gdb_path.split('/')[:-1]) + '/{0}_result_{1}.csv'.format(destination.split('_')[:-1][-1], time.replace(':',''))

		print outFile
		fields = ['Name', 'Total_Transit_TT']
		for lyr in arcpy.mapping.ListLayers(outNALayer):
			if lyr.name == linesLayerName:
				with open(outFile, 'w') as f:
					f.write(','.join(fields)+'\n') # csv headers
					with arcpy.da.SearchCursor(lyr, fields) as cursor:
						print "Successfully created lines searchCursor.  Exporting to " + outFile
						for row in cursor:
							f.write(','.join([str(r).replace(',',' ') for r in row])+'\n')

    	arcpy.Delete_management(outNALayer)

	arcpy.CheckInExtension("Network")


def process_results(destination, dayofweek, starttime):
	import pandas as pd, numpy as np, os, sys

	# run this in the same folder as the results files generated with network_analyst.py
	results = [x for x in os.listdir(os.getcwd()) if x.endswith(".csv") and x.startswith(destination)]
	minTT_df = pd.DataFrame()
	total_df = pd.DataFrame()
	for result in results:
		time = result.split('_')[-1].split('.')[0]
		df = pd.read_csv(result)
		df['ori'],df['dest'] = zip(*df['Name'].apply(lambda x: x.split(' - ',1)))
		df.drop('Name', inplace=True, axis=1)
		minTT_series = df.groupby(['ori'], sort=False)['Total_Transit_TT'].min()
		total_series = df.groupby(['ori'], sort=False)['Total_Transit_TT'].count()
		minTT_df['result_{0}'.format(time)] = np.round(minTT_series,2)
		total_df['result_{0}'.format(time)] = total_series
		total_df['hi_access'] = total_df[total_df.columns].max(axis=1)
		minTT_df['lo_transittime'] = minTT_df[minTT_df.columns].min(axis=1)

	total_df.to_csv('{0}_{1}{2}_total.csv'.format(destination, dayofweek[3:], starttime), columns=['hi_access'])
	minTT_df.to_csv('{0}_{1}{2}_minTT.csv'.format(destination, dayofweek[3:], starttime), columns=['lo_transittime'])

if __name__ == '__main__':
	process_results('super','Mon','12PM')
