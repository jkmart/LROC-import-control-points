# LUNAR RECONNAISSANCE ORBITER CAMERA                                         
### Arizona State University    
Python program that takes MatLab output from LOLA (Lunar Orbiter Laser Altimeter) registration and inputs into BAE SocetSet Ground Point File (.gpf).

The LOLA text files are example outputs from LROC Matlab DTM (Digital Terrain Model) registration using LOLA data points.

Based on University of Arizona registration program for SocetSet            
Import Control Points from Matlab registration                              
Usage: importControlPoints [options] projectName                            
           ctrlPointFile [ctrlPointFiles...]                                 
 Options: -d [SocetSetDataDirectory] -vha                                    
          -d [SocetSetDataDirectory] or --directory:                         
             [SocetSetDataDirectory] sets the script to run in the           
             Socet Set Data directory [SocetSet Program Path]/data/        
             E.g. C:\SOCET_SET_5.5.0\data\                                   
          -h displays this help text.                                        
          -v gives verbose messages                                          
          -a used when implementing with AutoIt/Pipeline                     
             which uses the format CTRLFILE_1|CTRLFILE_2|...|CTRLFILE_N  
