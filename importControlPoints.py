###############################################################################
# LUNAR RECONNAISSANCE ORBITER CAMERA                                         #
# Arizona State University                                                    #
# Author: J. Kerry Martin                                                     #
# Based on University of Arizona registration program for SocetSet            #
# Import Control Points from Matlab registration                              #
# Usage: importControlPoints [options] projectName                            #
#           ctrlPointFile [ctrlPointFiles...]                                 #
# Options: -d [SocetSetDataDirectory] -vha                                    #
#          -d [SocetSetDataDirectory] or --directory:                         #
#             [SocetSetDataDirectory] sets the script to run in the           #
#             Socet Set Data directory [SocetSet Program Path]/data/          #
#             E.g. C:\SOCET_SET_5.5.0\data\                                   #
#          -h displays this help text.                                        #
#          -v gives verbose messages                                          #
#          -a used when implementing with AutoIt/Pipeline                     #
#             which uses the format CTRLFILE_1|CTRLFILE_2|...|CTRLFILE_N      #
# TODO: Write Move To Point coords to a file if using AutoIt/Pipeline         #
###############################################################################

import getopt
import math
import os
import shutil
import sys


###############################################################################
# Functions                                                                   #
###############################################################################

def append_control_points(gpf, ctrl, point_number, use_box):
    # Takes an opened gpf file in append mode, then writes the relevant
    # control points from MatLab LOLA registration to the end of it,
    # using the control file name in the control point name
    read_file = open(ctrl, "r")
    # Get file name for appending to sequence number
    ctrl_name, ctrl_name_ext = os.path.splitext(os.path.basename(ctrl))

    while 1:
        line = read_file.readline()
        # Looping until the end of the file
        if not line:
            print("End of file")
            break
        line = line.strip()
        # Look for control point
        if line and ("Control Point:" in line):
            # Lat/lon/elevation data on next line
            line = read_file.readline()
            line = line.strip()
            # Convert the values and return an array
            coordinates = convert_coordinates(line)
            # Write to gpfFile
            point_number = write_coordinates(gpf, coordinates, point_number, ctrl_name, use_box)
    read_file.close()
    return point_number


def convert_coordinates(convert_string):
    # This function provided in the UofA autoTriangulation script
    # (Though at the time it wasn't a function)
    # This converts the output of the LOLA registration
    # to decimal degrees and then rads, which is used in the .gpf
    conversion = convert_string.split()
    # Debug text printing
    print(conversion[:2])
    print(conversion[2:4])
    print(conversion[4:])

    lon = conversion[1].split(":")
    min_to_dec = float(lon[1]) / 60.0
    sec_to_dec = float(lon[2]) / 3600.0

    if float(lon[0]) < 0:
        lon = math.pi / 180.0 * (float(lon[0]) - min_to_dec - sec_to_dec)
    elif float(lon[0]) >= 0:
        lon = math.pi / 180.0 * (float(lon[0]) + min_to_dec + sec_to_dec)
    else:
        print("Error in radian to DMS conversion.")
        sys.exit()
    lat = conversion[3].split(":")
    min_to_dec = float(lat[1]) / 60.0
    sec_to_dec = float(lat[2]) / 3600.0

    if float(lat[0]) < 0:
        lat = math.pi / 180.0 * (float(lat[0]) - min_to_dec - sec_to_dec)
    elif float(lat[0]) >= 0:
        lat = math.pi / 180.0 * (float(lat[0]) + min_to_dec + sec_to_dec)
    else:
        print("Error in radian to DMS conversion.")
        sys.exit()
    ht = float(conversion[5])
    converted = [lat, lon, ht]
    return converted


def write_coordinates(write_to_gpf, coordinates, sequence_number, control_name, use_box):
    # Write the coordinates to gpf file using gpf convention
    # This function assumes gpf has been opened already, and that
    # the gpf parameter is an open file object, coords is a list
    # of [lat, lon, elev] in rads, and gpfPointNum is global variable
    # that tracks the next point number in gpf
    # Write the point id, the "Use" box flag, and point type (XYZ control)
    if use_box:
        write_to_gpf.write(str(sequence_number) + "_" + control_name + " 1 3")
    else:
        write_to_gpf.write(str(sequence_number) + "_" + control_name + " 0 3")

    # Increment sequenceNumber immediately after writing, so that the
    # next write_coordinates call is correct. This also ensures that the
    # sequenceNumber is also going to be one higher that the last
    # input point, which is good for writing the total number of points
    # at the end
    sequence_number += 1

    # Format the lat/lon/height so that they match the formatting within .gpf
    lat = '{0:.14f}'.format(coordinates[0])
    lon = '{0:.14f}'.format(coordinates[1])
    ht = '{0:.14f}'.format(coordinates[2])
    # Write to .gpf using format present within the file
    write_to_gpf.write("\n" + lat + 8 * " " + lon + 8 * " " + ht)
    # Use standard LROC values for accuracy on XYZ control points
    write_to_gpf.write("\n20.000000 20.000000 1.000000")
    # No offset (until manual move-to-point and auto-two)
    write_to_gpf.write("\n0.000000 0.000000 0.000000")
    # Newline for next call
    write_to_gpf.write("\n\n")

    return sequence_number


def usage():
    # Print the usage information, detailing the order of options
    # and arguments as well as a short description of what the options do
    print("Usage: importControlPoints [options] projectName" +
          "ctrlPointFile [ctrlPointFiles...]" +
          "\nOptions: -d [SocetSetDataDirectory] -h -v " +
          "\n\t-d [SocetSetDataDirectory] or --directory:" +
          "[SocetSetDataDirectory] sets the script to run in the" +
          "Socet Set Data directory [SocetSet Program Path]/data/" +
          "\n\t-h displays this help text." +
          "\n\t-v gives verbose messages" +
          "\n\t-a used when implementing with AutoIt/Pipeline")
    raw_input("Press any key to continue...")
    return 0


##############################################################################
# Main program                                                               #
##############################################################################

def main():
    # This path must be set to the [Socet Set]/data directory
    # Alternatively, the directory path can be set using option -d [path]
    base_socet_directory = os.path.normpath(
        "C:/Users/socetset/Test/importControlPoints/")
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
        verbose = False
        autoit = False
        for o, a in opts:
            if o == "-v":
                print("Verbose Mode=On")
                verbose = True
            elif o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-d", "--directory"):
                base_socet_directory = a
            elif o == "-a":
                autoit = True
            else:
                assert False, "unhandled option"
        number_arguments = len(args)
    elif len(sys.argv) == 0:
        usage()
        sys.exit()
    else:
        print("Error importControlPoints failed. Usage \"importControlPoints" +
              "[options] projectName ctrlPointFile [ctrlPointFiles...]\"")
        sys.exit()
    # Variable placeholders for gpf file
    # and the control files output by MatLab registration
    control_files = []

    ############################################################################
    # Extracts file names and types + options                                  #
    ############################################################################

    # Check to make sure base_socet_directory is valid. If not, error out
    if not os.path.lexists(base_socet_directory):
        print("The specified Socet Set directory cannot be found.")
        sys.exit(2)

    # Extracts the Project Name from the first input parameter
    project_name = args[0]
    # Adding project directory [09Mar2015]
    project_directory = os.path.abspath(base_socet_directory + "/" + project_name)
    print("Project Name is: " + project_name + "\n")

    # Check path to directory to make sure it is valid
    if not os.path.lexists(project_directory):
        print("Project path " + project_directory +
              " does not seem to be a valid path.")
        sys.exit(2)
    elif verbose:
        print("Project path is " + project_directory)

    # Get the array of control files
    # If using AutoIt/Pipeline, we have a special format
    control_file_directory = ""
    if autoit:
        # From AutoIt docs: "the full path of the file(s) chosen.
        # Results for multiple selections are "Directory|file1|file2|...".
        temp_files = args[1].split("|")
        control_file_directory = temp_files[0]
        for i in temp_files[1:]:
            control_files.append(i)
    else:
        for i in args[1:number_arguments]:
            control_files.append(i)

    # Get the .gpf file from project folder. Quit if not found
    gpf_location = os.path.normpath(project_directory + "/" +
                                    project_name + ".gpf")
    if os.path.isfile(gpf_location):
        print("Found " + project_name + ".gpf in " + gpf_location)
        gpf_file = gpf_location
    else:
        print("Did not find " + project_name + ".gpf in " + gpf_location)
        print("Please ensure project name is correct and gpf file is in")
        print("the project directory, then try again.")
        sys.exit()

    # Create a backup gpf file in the project directory in case things go wrong
    # Using shutil.copy2(src, dst) as an attempt to preserve metadata
    gpf_backup, gpf_ext = os.path.splitext(gpf_file)
    gpf_backup += "_backup" + gpf_ext
    shutil.copy2(gpf_file, gpf_backup)

    # Create a temp file to write to
    temp_gpf, gpf_ext = os.path.splitext(gpf_file)
    temp_gpf += "_temp" + gpf_ext
    shutil.copy(gpf_file, temp_gpf)

    # Get the next point ID from gpf so that the control points will be
    # sequential after the last point in the file
    try:
        if verbose:
            print("Opening " + gpf_file + " for reading.")
        read_gpf = open(gpf_file, "r")
    except IOError, e:
        print("There was an error opening the file " + gpf_file)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()

    # Using the second line in gpf that contains
    # the number of points as the next point id
    read_gpf.readline()
    try:
        if verbose:
            print("Reading " + gpf_file + " for number of points (2nd line)")
        original_number_gpf_points = int(read_gpf.readline().strip())
    except ValueError:
        print("There was not an acceptable integer value on the second line")
        print("of the gpf file. This error is unhandled and program is exiting")
        sys.exit()
    read_gpf.close()
    gpf_point_number = original_number_gpf_points

    # Opening the gpf_file for appending so that we don't open/close for every
    # control point file
    try:
        if verbose:
            print("Opening " + temp_gpf + " to append point data.")
        append_gpf = open(temp_gpf, "a")
    except IOError, e:
        print("There was an error opening the file " + gpf_file)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()

    # Read in the MatLab registration output for LOLA control points, and
    # append the .gpf file with control point data
    # TODO: Set optional argument to decide if control point "Use" box in
    # Socet Set is checked or not. Default is unchecked
    # TODO: Do initial check on control files before appending any points
    # to the gpf
    for i in control_files:
        if verbose:
            print("Getting control points from " + i)
        if os.path.lexists(i):
            gpf_point_number = append_control_points(append_gpf, i,
                                                     gpf_point_number, False)
        else:
            print("Absolute path for " + i + " was not found")
            # Check if the abs path is given in AutoIt format
            if autoit:
                control_file_path = os.path.normpath(control_file_directory + "/" + i)
                if os.path.lexists(control_file_path):
                    print("Found " + control_file_path)
                    gpf_point_number = append_control_points(
                        append_gpf, control_file_path, gpf_point_number, False)
                else:
                    control_file_path = os.path.normpath(project_directory + "/" + i)
                    print("Attempting relative path within project directory: " +
                          control_file_path)
                    if os.path.lexists(control_file_path):
                        print("Found " + i + " in the project directory at" +
                              control_file_path)
                        gpf_point_number = append_control_points(
                            append_gpf, control_file_path, gpf_point_number, False)
                    else:
                        print("The control points file " + i + " was not found.")
                        sys.exit()
    # Close the gpf_file
    if verbose:
        print("Closing " + temp_gpf + " now that control points have been added")
    append_gpf.close()

    # Replace the point count with the new point count on second line of gpf
    print("New number of points: " + str(gpf_point_number))
    try:
        if verbose:
            print("Opening " + temp_gpf +
                  " to update the total number of points")
        write_gpf = open(temp_gpf)
    except IOError, e:
        print("There was an error opening the file " + temp_gpf)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()
    # Read first line
    first_line = write_gpf.readline()
    # Read second line
    second_line = write_gpf.readline()
    # Replace original value with updated one
    new_second_line = second_line.replace(
        str(original_number_gpf_points), str(gpf_point_number))
    # Get the rest of the lines from the file, then write
    rest = ''.join(write_gpf.readlines())
    if verbose:
        print("Closing " + temp_gpf)
    write_gpf.close()
    try:
        write_gpf = open(temp_gpf, 'w')
    except IOError, e:
        print("There was an error opening the file " + temp_gpf)
        print("The file is missing or there is some other problem opening it")
        print(e)
        sys.exit()
    write_gpf.write(first_line + new_second_line + rest)
    write_gpf.close()

    # Write the temp file to main gpf file, then delete the temp
    print("\nMoving temp file to the primary .gpf file, then removing temp")
    os.remove(gpf_file)
    os.renames(temp_gpf, gpf_file)


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
