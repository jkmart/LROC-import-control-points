###############################################################################
# LUNAR RECONNAISSANCE ORBITER CAMERA                                         #
# Import Control Points from Matlab registration                              #
# Usage: importControlPoints [options] projectName                            #
#           ctrlPointFile [ctrlPointFiles...]                                 #
# Options: -d [SocetSetDataDirectory] -vha                                    #
#          -d [SocetSetDataDirectory] or --directory:                         #
#             [SocetSetDataDirectory] sets the script to run in the           #
#             Socet Set Data directory [SocetSet Program Path]/data/          #
#             E.g. C:\SOCET_SET_5.5.0\data\
#          -h displays this help text.                                        #
#          -v gives verbose messages                                          #
#          -a used when implementing with AutoIt/Pipeline                     #
#             which uses the format CTRLFILE_1|CTRLFILE_2|...|CTRLFILE_N      #
# TODO: Write Move To Point coords to a file if using AutoIt/Pipeline         #
###############################################################################

import sys
import os
import math
import shutil
import getopt

###############################################################################
# Functions                                                                   #
###############################################################################

def appendControlPoints(gpf, ctrl, pointNum, useBox):
    # Takes an opened gpf file in append mode, then writes the relevant
    # control points from Matlab LOLA registration to the end of it,
    # using the control file name in the control point name
    readFile = open(ctrl, "r")
    # Get file name for appending to sequence number
    ctrlName, ctrlNameExt = os.path.splitext(os.path.basename(ctrl))

    while 1:
        line = readFile.readline()
        # Looping until the end of the file
        if not line:
           print("End of file")
           break
        line = line.strip()
        # Look for control point
        if line and (("Control Point:") in line):
            # Lat/lon/elevation data on next line
            line = readFile.readline()
            line = line.strip()
            # Convert the values and return an array
            coords = convertCoordinates(line)
            # Write to gpfFile
            pointNum = writeCoords(gpf, coords, pointNum, ctrlName, useBox)
    readFile.close()
    return pointNum

def convertCoordinates(convertString):
    # This function provided in the UofA autoTriangulation script
    # (Though at the time it wasn't a function)
    # This converts the output of the LOLA registration
    # to decimal degrees and then rads, which is used in the .gpf
    conversion = convertString.split()
    # Debug text printing
    print(conversion[:2])
    print(conversion[2:4])
    print(conversion[4:])

    lon = conversion[1].split(":")
    min_to_dec = float(lon[1])/60.0
    sec_to_dec = float(lon[2])/3600.0

    if float(lon[0]) < 0:
        lon = math.pi/180.0*(float(lon[0]) - min_to_dec - sec_to_dec)
    elif float(lon[0]) >= 0:
        lon = math.pi/180.0*(float(lon[0]) + min_to_dec + sec_to_dec)
    else:
        print("Error in radian to DMS conversion.")
        sys.exit()
    lat = conversion[3].split(":")
    min_to_dec = float(lat[1])/60.0
    sec_to_dec = float(lat[2])/3600.0

    if float(lat[0]) < 0:
        lat = math.pi/180.0*(float(lat[0]) - min_to_dec - sec_to_dec)
    elif float(lat[0]) >= 0:
        lat = math.pi/180.0*(float(lat[0]) + min_to_dec + sec_to_dec)
    else:
        print("Error in radian to DMS conversion.")
        sys.exit()
    ht = float(conversion[5])
    converted = [lat, lon, ht]
    return converted

def writeCoords(writeTo, coords, seqNum, ctrlName, useBox):
    # Write the coordinates to gpf file using gpf convention
    # This function assumes gpf has been opened already, and that
    # the gpf parameter is an open file object, coords is a list
    # of [lat, lon, elev] in rads, and gpfPointNum is global variable
    # that tracks the next point number in gpf
    # Write the point id, the "Use" box flag, and point type (XYZ control)
    if useBox:
        writeTo.write(str(seqNum) + "_" + ctrlName + " 1 3")
    else:
        writeTo.write(str(seqNum) + "_" + ctrlName + " 0 3")

    # Increment sequenceNumber immediately after writing, so that the
    # next writeCoords call is correct. This also ensures that the
    # sequenceNumber is also going to be one higher that the last
    # input point, which is good for writing the total number of points
    # at the end
    seqNum += 1

    # Format the lat/lon/ht so that they match the formatting within .gpf
    lat = '{0:.14f}'.format(coords[0])
    lon = '{0:.14f}'.format(coords[1])
    ht = '{0:.14f}'.format(coords[2])
    # Write to .gpf using format present within the file
    writeTo.write("\n" + lat + 8*" " + lon + 8*" " + ht)
    # Use standard LROC values for accuracy on XYZ control points
    writeTo.write("\n20.000000 20.000000 1.000000")
    # No offset (until manual move-to-point and auto-two)
    writeTo.write("\n0.000000 0.000000 0.000000")
    # Newline for next call
    writeTo.write("\n\n")

    return seqNum

def usage():
    # Print the usage information, detailing the order of options
    # and arguments as well as a short description of what the options do
    print("Usage: importControlPoints [options] projectName"
        + "ctrlPointFile [ctrlPointFiles...]"
        + "\nOptions: -d [SocetSetDataDirectory] -h -v "
        + "\n\t-d [SocetSetDataDirectory] or --directory:"
        + "[SocetSetDataDirectory] sets the script to run in the"
        + "Socet Set Data directory [SocetSet Program Path]/data/"
        + "\n\t-h displays this help text."
        + "\n\t-v gives verbose messages"
        + "\n\t-a used when implementing with AutoIt/Pipeline")
    raw_input("Press any key to continue...")
    return 0


##############################################################################
# Main program                                                               #
##############################################################################

def main():
    # This path must be set to the [Socet Set]/data directory
    # Alternatively, the directory path can be set using option -d [path]
    BaseSocetDirectory = os.path.normpath(
    "C:/Users/socetset/Test/importControlPoints/")
    numArg = 0
    verbose = False
    # Get the input options and arguments
    if len(sys.argv) > 1:
        print("Running importControlPoints")
        try:
            opts, args = getopt.getopt(sys.argv[1:], "ahd:v",
            ["help", "directory="])
            print("Options list: " + str(opts))
        except getopt.GetoptError, err:
            # print help information and exit:
            # will print something like "option -a not recognized"
            print str(err)
            usage()
            sys.exit(2)
        output = None
        verbose = False
        autoIt = False
        for o, a in opts:
            if o == "-v":
                    print("Verbose Mode=On")
                    verbose = True
            elif o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-d", "--directory"):
               BaseSocetDirectory = a
            elif o == "-a":
                autoIt = True
            else:
                assert False, "unhandled option"
        numArg = len(args)
    elif len(sys.argv) == 0:
        usage()
        sys.exit()
    else:
        print("Error importControlPoints failed. Usage \"importControlPoints" +
        "[options] projectName ctrlPointFile [ctrlPointFiles...]\"")
        sys.exit()
    # Variable placeholders for gpf file
    # and the control files output by MatLab registration
    gpfFile = ""
    controlfiles = []
    gpfPointNum = 0

    ############################################################################
    # Extracts file names and types + options                                  #
    ############################################################################

    # Check to make sure BaseSocetDirectory is valid. If not, error out
    if not os.path.lexists(BaseSocetDirectory):
        print("The specified Socet Set directory cannot be found.")
        sys.exit(2)

    # Extracts the Project Name from the first input parameter
    ProjectName = args[0]
    # Adding project directory [09Mar2015]
    ProjectDirectory = os.path.abspath(BaseSocetDirectory + "/" + ProjectName)
    print("Project Name is: " + ProjectName + "\n")

    # Check path to directory to make sure it is valid
    if not os.path.lexists(ProjectDirectory):
        print("Project path " + ProjectDirectory +
        " does not seem to be a valid path.")
        sys.exit(2)
    elif (verbose):
            print("Project path is " + ProjectDirectory)

    # Get the array of control files
    # If using AutoIt/Pipeline, we have a special format
    if autoIt:
        # From AutoIt docs: "the full path of the file(s) chosen.
        # Results for multiple selections are "Directory|file1|file2|...".
        tempFiles = args[1].split("|")
        ctrlFileDir = tempFiles[0]
        for ctrlFile in tempFiles[1:]:
            controlfiles.append(ctrlFile)
    else:
        for ctrlFile in args[1:numArg]:
            controlfiles.append(ctrlFile)

    # Get the .gpf file from project folder. Quit if not found
    gpfLocation = os.path.normpath(ProjectDirectory + "/" +
    ProjectName + ".gpf")
    if (os.path.isfile(gpfLocation)):
        print("Found " + ProjectName + ".gpf in " + gpfLocation)
        gpfFile = gpfLocation
    else:
        print("Did not find " + ProjectName + ".gpf in " + gpfLocation)
        print("Please ensure project name is correct and gpf file is in")
        print("the project directory, then try again.")
        sys.exit()

    # Create a backup gpf file in the project directory in case things go wrong
    # Using shutil.copy2(src, dst) as an attempt to preserve metadata
    gpfBackup, gpfExt = os.path.splitext(gpfFile)
    gpfBackup += "_backup" + gpfExt
    shutil.copy2(gpfFile, gpfBackup)

    # Create a temp file to write to
    gpfTemp, gpfExt = os.path.splitext(gpfFile)
    gpfTemp += "_temp" + gpfExt
    shutil.copy(gpfFile, gpfTemp)

    # Get the next point ID from gpf so that the control points will be
    # sequential after the last point in the file
    try:
        if verbose:
            print("Opening " + gpfFile + " for reading.")
        gpfRead = open(gpfFile, "r")
    except IOError, e:
        print("There was an error opening the file " + gpfFile)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()

    # Using the second line in gpf that contains
    # the number of points as the next point id
    gpfRead.readline()
    try:
        if verbose:
            print("Reading " + gpfFile + " for number of points (2nd line)")
        gpfPointNumOriginal = int(gpfRead.readline().strip())
    except ValueError:
        print("There was not an acceptable integer value on the second line")
        print("of the gpf file. This error is unhandled and program is exiting")
        sys.exit()
    gpfRead.close()
    gpfPointNum = gpfPointNumOriginal

    # Opening the gpfFile for appending so that we don't open/close for every
    # control point file
    try:
        if verbose:
            print("Opening " + gpfTemp + " to append point data.")
        gpfAppend = open(gpfTemp, "a")
    except IOError, e:
        print("There was an error opening the file " + gpfFile)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()

    # Read in the MatLab registration output for LOLA control points, and
    # append the .gpf file with control point data
    # TODO: Set optional argument to decide if control point "Use" box in
    # Socet Set is checked or not. Default is unchecked
    # TODO: Do initial check on control files before appending any points
    # to the gpf
    for ctrlFile in controlfiles:
        if verbose:
            print("Getting control points from " + ctrlFile)
        if os.path.lexists(ctrlFile):
            gpfPointNum = appendControlPoints(gpfAppend, ctrlFile,
            gpfPointNum, False)
        else:
            print("Absolute path for " + ctrlFile + " was not found")
                # Check if the abs path is given in AutoIt format
            if autoIt:
                ctrlFilePath = os.path.normpath(ctrlFileDir + "/" + ctrlFile)
                if os.path.lexists(ctrlFilePath):
                    print("Found " + ctrlFilePath)
                    gpfPointNum = appendControlPoints(gpfAppend, ctrlFilePath,
                                                      gpfPointNum, False)
                else:
                    ctrlFilePath = os.path.normpath(ProjectDirectory+"/"+ctrlFile)
                    print("Attempting relative path within project directory: " +
                    ctrlFilePath)
                    if os.path.lexists(ctrlFilePath):
                        print("Found " + ctrlFile + " in the project directory at" +
                        ctrlFilePath)
                        gpfPointNum = appendControlPoints(gpfAppend, ctrlFilePath,
                        gpfPointNum, False)
                    else:
                        print("The control points file " + ctrlFile + " was not found.")
                        sys.exit()
    # Close the gpfFile
    if verbose:
        print("Closing " + gpfTemp + " now that control points have been added")
    gpfAppend.close()

    # Replace the point count with the new point count on second line of gpf
    print("New number of points: " + str(gpfPointNum))
    try:
        if verbose:
            print("Opening " + gpfTemp +
            " to update the total number of points")
        gpfWrite = open(gpfTemp)
    except IOError, e:
        print("There was an error opening the file " + gpfTemp)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()
    # Read first line
    firstLine = gpfWrite.readline()
    # Read second line
    secondLine = gpfWrite.readline()
    # Replace original value with updated one
    newSecondLine = secondLine.replace(str(gpfPointNumOriginal),
    str(gpfPointNum))
    # Get the rest of the lines from the file, then write
    rest = ''.join(gpfWrite.readlines())
    if verbose:
        print("Closing " + gpfTemp)
    gpfWrite.close()
    try:
        gpfWrite = open(gpfTemp, 'w')
    except IOError, e:
        print("There was an error opening the file " + gpfTemp)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()
    gpfWrite.write(firstLine+newSecondLine+rest)
    gpfWrite.close()

    # Write the temp file to main gpf file, then delete the temp
    print("\nMoving temp file to the primary .gpf file, then removing temp")
    os.remove(gpfFile)
    os.renames(gpfTemp, gpfFile)

# Run main()
if __name__ == "__main__":
    try:
        main()
    except:
        import sys
        print sys.exc_info()[0]
        import traceback
        print traceback.format_exc()
    finally:
        print "Finishing up ..."
        raw_input("Press Enter to continue")
