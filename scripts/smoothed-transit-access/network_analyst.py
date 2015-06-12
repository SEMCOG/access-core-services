import arcpy, os
arcpy.env.workspace = 'C:/Users/mcbroom/Desktop/access.gdb'

if arcpy.CheckExtension("Network") == "Available":
	arcpy.CheckOutExtension("Network")
	print "Network analyst license available"
else:
	print "Network license unavailable"

start_times = ['8:{0}'.format(str(x).zfill(2)) for x in xrange(30)]

for time in start_times:
    eval_time = "6/1/2015 {0}:00 AM".format(time)
    
    print "Making OD Cost Matrix Layer for {0}".format(eval_time)
    
    outNALayer = arcpy.MakeODCostMatrixLayer_na(in_network_dataset="C:/Users/mcbroom/Desktop/access.gdb/semTransit/semTransit_ND",
                                    out_network_analysis_layer="OD Cost Matrix",
                                    impedance_attribute="Transit_TT",
                                    default_cutoff="30",
                                    default_number_destinations_to_find="#",
                                    accumulate_attribute_name="#",
                                    UTurn_policy="ALLOW_UTURNS",
                                    restriction_attribute_name="#",
                                    hierarchy="NO_HIERARCHY",
                                    hierarchy_settings="#",
                                    output_path_shape="NO_LINES",
                                    time_of_day=eval_time)
    
    print "Made OD Cost Matrix Layer"
    
    outNALayer = outNALayer.getOutput(0)
    
    subLayerNames = arcpy.na.GetNAClassNames(outNALayer)
    
    originsLayerName = subLayerNames["Origins"]
    destinationsLayerName = subLayerNames["Destinations"]
    linesLayerName = subLayerNames["ODLines"]
    
    print "Adding Destinations"
    
    # add grocery stores
    arcpy.AddLocations_na(in_network_analysis_layer="OD Cost Matrix",
                            sub_layer="Destinations",
                            in_table="destination_grocery_super",
                            field_mappings="Name Establishm #",
                            search_tolerance="5000 Meters",
                            sort_field="#",
                            search_criteria="Connectors_Stops2Streets NONE;Streets_UseThisOne SHAPE;TransitLines NONE;Stops NONE;Stops_Snapped2Streets NONE;semTransit_ND_Junctions NONE",
                            match_type="MATCH_TO_CLOSEST",
                            append="APPEND",
                            snap_to_position_along_network="NO_SNAP",
                            snap_offset="5 Meters",
                            exclude_restricted_elements="INCLUDE",
                            search_query="Connectors_Stops2Streets #;Streets_UseThisOne #;TransitLines #;Stops #;Stops_Snapped2Streets #;semTransit_ND_Junctions #")
    
    # add origins
    print "Adding origins"
    arcpy.AddLocations_na(in_network_analysis_layer="OD Cost Matrix",sub_layer="Origins",in_table="origin_naTransitCentroids",field_mappings="Name nodeid #",search_tolerance="5000 Meters",sort_field="#",search_criteria="Connectors_Stops2Streets NONE;Streets_UseThisOne SHAPE;TransitLines NONE;Stops NONE;Stops_Snapped2Streets NONE;semTransit_ND_Junctions NONE",match_type="MATCH_TO_CLOSEST",append="APPEND",snap_to_position_along_network="NO_SNAP",snap_offset="5 Meters",exclude_restricted_elements="INCLUDE",search_query="Connectors_Stops2Streets #;Streets_UseThisOne #;TransitLines #;Stops #;Stops_Snapped2Streets #;semTransit_ND_Junctions #")
    
    print "Begin Solving"
    arcpy.na.Solve(outNALayer)
    print "Done Solving"
    outFile = 'C:\Users\mcbroom\Desktop\super_result_{0}.csv'.format(time.replace(':',''))
    fields = ['Name', 'Total_Transit_TT']
    for lyr in arcpy.mapping.ListLayers(outNALayer):
        if lyr.name == linesLayerName:
            with open(outFile, 'w') as f:
                f.write(','.join(fields)+'\n') # csv headers
                with arcpy.da.SearchCursor(lyr, fields) as cursor:
                    print "Successfully created lines searchCursor.  Exporting to " + outFile
                    for row in cursor:
                        f.write(','.join([str(r) for r in row])+'\n')
                        
    arcpy.Delete_management(outNALayer)
    
arcpy.CheckInExtension("Network")

