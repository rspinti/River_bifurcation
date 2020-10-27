# Problematic dams
We discovered that many dams with large storage values did not exist in NABD. This included
the Hoover Dam, which is a key dam in the analysis of the Colorado River Basin.
Despite this issue, we decided to continue with NABD because it contains fewer
duplicates and errors than NID. This was confirmed when we performed a manual
check on 171 large storage dams that were missing from NABD. Many of the NID dams
had the same ID and storage value but were listed as separate dams.

Large dams were considered to be those with storage values greater or equal to the
GRanD threshold for storage 0.1 km^3. We obtained 171 dams that fit these requirements
by joining NABD to NID on NIDID in python and then filtering out all the dams that
did not have a COMID. Of the 171 dams, 56 had the wrong NIDID. The remainder did
not appear in NABD at all (manual check to find matching names).

### Updated dams
These are dams that had the wrong NIDID in NABD, which is why they appeared to be missing.
Dams that had the shared a NIDID in NID were considered to be one dam. The csv file
titled 'large_dams_wrongID' contains all these dams and their correct NIDID.

ALTUS AUXILIARY DIKE
ALTUS EAST DIKE
ALTUS LUGERT DIKE
ALTUS NORTH DIKE
ALTUS SOUTH DIKE
ARBUCKLE DIKE 1
ARBUCKLE DIKE 2
BUENA VISTA
BURTON
CHATUGE
CLAYTOR
CUSHMAN NO. 1 SPILLWAY
DEGRAY SADDLE DIKE
G205 CONTROL STRUCTURE
G206 CONTROL STRUCTURE
G335 CONTROL STRUCTURE
G338 CONTROL STRUCTURE
G94B CONTROL STRUCTURE
G94C CONTROL STRUCTURE
GATHRIGHT DAM
GLENDO DIKE NO. 1
GLENDO DIKE NO. 2
GLENDO DIKE NO. 3
JOHN H KERR DAM
KENTUCKY
LAKE ANNA DAM AND RESERVOIR
LAKE ANNA DAM AND RESERVOIR - DIKE I
LAKE ANNA DAM AND RESERVOIR - DIKE II
LAKE ANNA DAM AND RESERVOIR - DIKE III
LAKE ANNA DAM AND RESERVOIR - DIKE V
LAKE ANNA DAM AND RESERVOIR - DIKE VI
LAKE DESMET (A,B,C & SPILLWAY DIKES)
LEESVILLE
LLOYD SHOALS
LLOYD SHOALS - EMERGENCY SPILLWAY
LLOYD SHOALS - NORTH SADDLE DIKE
LOCK & DAM #10
LOCK & DAM NO 10
PHILPOTT DAM
PUMPING STATION 129
PUMPING STATION 131 AND LOCK
PUMPING STATION 133
PUMPING STATION 135 AND LOCK
PUMPING STATION NO. 2
PUMPING STATION NO. 236
PUMPING STATION NO. 3
QUABBIN GOODNOUGH DIKE
ROUND VALLEY DIKE
SEVEN OAKS
SHADEHILL DIKE NO.1
SMITH MOUNTAIN COMBINATION PUMP STORAGE
SUGAR LOAF
SUGAR LOAF DIKE
TIBER DIKE
WALLACE
WALLACE SADDLE DIKE

### New dams
The dams that are considered new are ones that do not exist in NABD, but exist in
NID. They are contained in the csv file titled 'large_dams_to_add'.

- Conowingo (MD) - There are two dams next to each other with same name and different storage.
