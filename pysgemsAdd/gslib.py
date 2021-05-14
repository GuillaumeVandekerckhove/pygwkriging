import numpy as np
from loguru import logger


def main(inputfile, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input, outputfolder):
    """ Function to add the coordinates to the gslib file that was the result of kriging. """
    logger.info(f'Adding the coordinates to the kriging results.')
    # get the inputfilename and the location of the output folder
    inputfile = inputfile
    inputfile = inputfile.replace("\\", "/")
    inputfile = inputfile.replace('"', '')
    inputfilename = inputfile.split('resultsdata2d')
    a = inputfilename[1]
    b = inputfilename[2]
    b = b.strip('/')
    inputfilename = a + 'resultsdata2d' + b
    outputfolder = outputfolder.replace("\\", "/")
    outputfolder = outputfolder.replace('"', '')

    # create the dimensions
    nx = (x_lim_input-x0_input)/dx_input  # number of cells in x direction
    ny = (y_lim_input-y0_input)/dy_input  # number of cells in y direction
    nz = 1  # number of cells in the z direction
    dx = dx_input  # the dimension of a cell in the x direction
    dy = dy_input  # the dimension of a cell in the y direction
    dz = 0  # the dimension of a cell in the z direction
    x0 = x0_input  # the x coordinate of the origin cell
    y0 = y0_input  # the y coordinate of the origin cell
    z0 = 0  # the z coordinate of the origin cell

    values = []

    # read the data of the input file
    with open(inputfile, "r") as f:
        rows = f.readlines()[1:]

    # creating a new file, without a header, only the data
    new_file = open(inputfile + "withouthead.txt", "w")
    for line in rows:
        for i in line:
            if i != ' ':
                None
            else:
                new_file.write(line)
                break
    new_file.close()
    inputfile = new_file.name

    # get the kriging values
    file = open(inputfile, 'r')
    lines = file.readlines()
    for line in lines:
        values.extend([line])

    # calculate the coordinates
    length = len(lines)
    ind = list(range(1, length+1))
    coordinates = []
    for i in ind:
        iz = 1+int((i-1)/(nx*ny))  # get the coordinate of z
        iy = 1+int((i-(iz-1)*nx*ny)/nx)  # get the coordinate of y
        ix = i-(iz-1)*nx*ny-(iy-1)*nx  # get the coordinate of x
        if ix == 0:
            x = x0 + (dx/2) + (nx-1)*dx
            y = y
            z = z
            coordinate = [x, y, z]
            coordinates.extend([coordinate])
        else:
            x = x0 + (dx/2) + (ix-1)*dx
            y = y0 + (dy/2) + (iy-1)*dy
            z = z0 + (dz/2) + (iz-1)*dz
            coordinate = [x, y, z]
            coordinates.extend([coordinate])
    file.close()

    # add the coordinates to the kriging results
    ind2 = list(range(0, length))
    results = []
    for i in ind2:
        a = [float(values[i])]
        list1 = coordinates[i] + a
        results.extend([list1])
    np.savetxt(outputfolder + inputfilename + '-xyz_value.txt', results, delimiter="\t", fmt="%s")
    logger.info(f'Saved the total results of kriging in the QGiS folder.')

    # Filter the results. Makes a new file without the -9966699.0 values.
    results_filtered = []
    for i in results:
        if i[3] == -9966699.0:
            None
        else:
            results_filtered.extend([i])
    if len(results) == len(results_filtered):
        None
    else:
        np.savetxt(outputfolder + inputfilename + '-xyz_value_filtered.txt', results_filtered, delimiter="\t", fmt="%s")
        logger.info(f'Saved the filtered results of kriging in the QGiS folder.')
