# Area 5 (FBO + cargo staff lots) - survey result: NO BUILD.
# North zone (s 300..348, t -100..-12): hangars + apron fill all of it; FBO (t -19..-12) is ringed by
#   apron (bizjet stand at t -25), the south connector taxiway (s 297..299) and grass outside the zone.
# Cargo zone (s -14..46, t -100..-27): landside is only the 1-wide service road at t=-100 with truck docks
#   on the warehouse west walls; fuel farm s -14..-4; ops office s -14..-7, t -52..-32; the only gaps are
#   s 16..19 (4 wide) between the warehouses, t -31..-27 (5 wide) east of the office, and the UPS
#   freighter stand / GSE apron north of the office. None fits a 3x7 bay plus a 7-wide aisle off a road.
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\plib.py").read())
report_bays()
