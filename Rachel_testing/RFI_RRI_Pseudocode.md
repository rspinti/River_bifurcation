# Pseudocode for calculation of RFI and RRI

## Variables that both use:
- total river volume of entire network
- river volume of reach/fragment

## RRI
- number of dams upstream
- storage capacity 
- total annual flow volume
- number of river reaches
- river volume of reach i
- total river volume of entire network

## RFI
- number of fragments
- total river volume of fragment
- total river volume of entire network

### Code
- Sum the river volume over each fragment in the basin
- Sum the total river volume in basin
- get count on # of fragments
- for each fragment use the equation to get RFI for that Frag ID

- get count of # of dams upstream
- Sum the storage of dams upstream on each reach
- get annual discharge of the reach
- get # of reaches in network/basin
- get river volumes of each reach and divide by river network volume