import os
import glob
import time
import shutil
import matplotlib.pyplot as plt
from os.path import join as jp
from pysgems.algo.sgalgo import XML
from pysgems.dis.sgdis import Discretize
from pysgems.io.sgio import PointSet
from pysgems.plot.sgplots import Plots
from pysgems.sgems import sg
#from pysgems.variogram import space_to_tab             import later from pysgems
#from pysgems.variogram import variogram_total          import later from pysgems
#from pysgems.gslib import gslib                        import later from pysgems
from loguru import logger

files = []
list1 = []

os.mkdir("programrun")  # create a folder where are the files can be placed to at the end of the program
os.mkdir("QGiS")  # create a folder where the results with the coordinates are saved
output = os.getcwd()
output1 = jp(output, "programrun")


def pydov(pydovdata):
    """ The function to get the data from DOV through pydov."""
    if pydovdata == 'yes':
        import dov.data_pydov as datapydov
        datapydov.main()  # run the script that downloads the data
        output2 = output.strip('script')
        inputtxtfile = jp(output, 'Input.txt')
        spacetotab(inputtxtfile,2)  # changes the spaces in the input.txt file to tab
        inputtxtfile = inputtxtfile + 'spacetotabs' + 'no_whiterules.txt'
        outputtxtfile = jp(output2, 'datafilter', 'Input.txt')
        shutil.move(inputtxtfile, outputtxtfile)  # places the file with the necessary input in the correct folder

    else:
        None


def filterdata(pydovdata):
    """ The function that filters the input data, created by pydov or a txt file """
    import datafilter.dataset_filter as data
    data.main(pydovdata)  # run the script that filters the data


def spacetotab(i, columns):
    """ Changes the seperator from space to tab in a text file.
    i = input file
    columns = how many columns the input file has (works for two and 4 columns)
    """
    import pysgemsAdd.space_to_tab as tab
    tab.main(i, columns)  # run the script that changes the seperator
    #space_to_tab.main(i)                               import later from pysgems


def joinStrings(stringList):
    """Add strings together to get one string."""
    return ''.join(string for string in stringList)


def getsgemsfiles():
    """ Function to get the files for kriging. """
    outputfile = os.getcwd()
    datafiles1 = glob.glob(outputfile + "/resultsdata2d//*.txt")
    datafilesperaquifer = []
    # create a list with all the datafiles per aquifer
    for i in datafiles1:
        result1 = [a.replace('\\', '/', 1) for a in i]
        result1 = joinStrings(result1)
        datafilesperaquifer.extend([result1])

    for i in datafilesperaquifer:
        if i[-9:] == 'sgems.txt':
            list1.extend([i])


def variogram(nbpoints):
    """ Function to create the variograms.
    nbpoints = the number of points that have to be displayed by the variogram
    """
    getsgemsfiles()  # get the files for kriging
    import pysgemsAdd.variogram_total as variogram

    for i in list1:
        # create a new file with only the data and no heading
        a_file = open(i, "r")
        lines = a_file.readlines()
        a_file.close()
        new_file = open(i+"withouthead.txt", "w")
        for line in lines:
            for i in line:
                if i != ' ':
                    None
                else:
                    new_file.write(line)
                    break
        new_file.close()
        inputfile = new_file.name
        spacetotab(inputfile, 4)  # change seperator from space to tab
        inputfile = inputfile + 'spacetotabsno_whiterules.txt'
        variogram.main(inputfile, nbpoints)  # run the script to make the variograms
        #variogram_total.main(inputfile, nbpoints)                  import later from pysgems


def coordinates(inputfile, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input):
    """ Function to add the coordinates to a gslib file that was the result of kriging. """
    import pysgemsAdd.gslib as gslib
    outputfolder = os.getcwd()
    outputfolder = jp(outputfolder, "QGiS")  # save the file to the QQGiS folder
    gslib.main(inputfile, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input, outputfolder)


def kriging(dataset):
    list2 = []
    # %% Initiate sgems pjt
    cwd = os.getcwd()  # Working directory
    resultdirectory = dataset.strip('_sgems.txt')
    rdir = resultdirectory  # Results directory
    pjt = sg.Sgems(project_name="sgems_test_G", project_wd=cwd, res_dir=rdir)

    # %% Load data point set

    file_path = dataset
    with open(file_path, "r") as f1:
        with open(file_path + '.eas', "w") as f2:
            f2.write(f1.read())
    file_path = file_path + '.eas'

    ps = PointSet(project=pjt, pointset_path=file_path)

    # %% Generate grid. Grid dimensions can automatically be generated based on the data points
    # unless specified otherwise, but cell dimensions dx, dy, (dz) must be specified

    area= input('Which area do you choose? Type flanders or other. \n')
    if area == 'flanders':

        dx_input = 100
        dy_input = 100
        x0_input = 20000
        y0_input = 150000
        x_lim_input = 260000
        y_lim_input = 250000

        ds = Discretize(project=pjt,
                        dx=dx_input,
                        dy=dy_input,
                        xo=x0_input,
                        yo=y0_input,
                        x_lim=x_lim_input,
                        y_lim=y_lim_input)

    else:
        dx_input = int(input('What is dx? '))
        dy_input = int(input('What is dy? '))
        x0_input = int(input('What is x0? '))
        y0_input = int(input('What is y0? '))
        x_lim_input = int(input('What is the limit of x? '))
        y_lim_input = int(input('What is the limit of y? '))

        ds = Discretize(project=pjt,
                        dx=dx_input,
                        dy=dy_input,
                        xo=x0_input,
                        yo=y0_input,
                        x_lim=x_lim_input,
                        y_lim=y_lim_input)

    # %% Display point coordinates and grid
    pl = Plots(project=pjt)
    pl.plot_coordinates()

    # %% Which feature are available
    # print(pjt.point_set.columns)

    # %% Load your algorithm xml file in the 'algorithms' folder.
    algo_dir = jp(cwd, "resultsdata2d")
    al = XML(project=pjt, algo_dir=algo_dir)
    xml_name = dataset + 'withouthead.txtspacetotabsno_whiterules.txtvariogram'

    splitstring = xml_name.split('resultsdata2d')
    substring = splitstring[1] + 'resultsdata2d' + splitstring[2]
    substring = substring.strip('/')
    xml_name = substring
    al.xml_reader(xml_name)

    # %% Show xml structure tree
    al.show_tree()

    # %% Modify xml below:
    # By default, the feature grid name of feature X is called 'X_grid'.
    # sgems.xml_update(path, attribute, new value)
    al.xml_update("Hard_Data", "grid", "parameter_grid")
    al.xml_update("Hard_Data", "property", "parameter")

    # %% Write binary datasets of needed features
    # sgems.export_01(['f1', 'f2'...'fn'])
    ps.export_01("parameter")

    # %% Write python script
    pjt.write_command()

    # %% Run sgems
    pjt.run()
    # Plot 2D results
    namekriging = "results"
    result_file_kriging = jp(rdir, namekriging + ".grid")
    save = "kriging"
    #pl.plot_2d(namekriging, save=save)
    pl.plot_2d(res_file=result_file_kriging, save=save)
    list2.extend([result_file_kriging])

    """
    Code for variance map (not yet in pysgems)
    
    namekrigingvar = "results(var)"
    result_file_kriging_variance = jp(rdir, namekrigingvar + ".grid")
    save = "kriging_var"
    #pl.plot_2d(namekrigingvar, save=save)
    pl.plot_2d(res_file=result_file_kriging_variance, save=save)
    plt.close()
    list2.extend([result_file_kriging_variance])
    
    """

    for i in list2:
        coordinates(i, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input)


def removefolder():
    """ Function to move al the files, that were made during the program, to the 'programrun' folder. """
    move = input('Do you want to remove the temporary files and the definitive folders? ')
    if move == 'yes':
        output3 = output.strip('script')
        aquiferall = jp(output, "aquiferall")
        aquiferhead = jp(output, "aquiferhead")
        resultsdata = jp(output, "resultsdata")
        resultsdata2d = jp(output, "resultsdata2d")
        year = jp(output, "year")
        inputfile2 = jp(output, "inputfile2")
        inputfile3 = jp(output, "inputfile3")
        inputfile4 = jp(output, "inputfile4")
        resultsdata2d_sgems = jp(output, "resultsdata2d_sgems")
        qgis = jp(output, "QGiS")
        inputtxt = jp(output3, "datafilter", "Input.txt")
        files.extend([aquiferall] + [aquiferhead] + [resultsdata] + [resultsdata2d] + [year] + [inputfile2] + [inputfile3] + [inputfile4] + [resultsdata2d_sgems] + [qgis] + [inputtxt])
        for f in files:
            shutil.move(f, output1)
        shutil.move(output1, output3)
    else:
        None


def run():
    """ Function to run the program. """
    start = time.time()
    pydovdata = input('Do you want to work with pydov or not? (yes/no) ')
    pydov(pydovdata)
    filterdata(pydovdata)
    nbpoints = input('How many points do you want the variogram to display? ')
    nbpoints = int(nbpoints)
    variogram(nbpoints)
    for i in list1:
        kriging(i)
    removefolder()
    logger.info(f"ran the full algorithm in {time.time() - start} s or {(time.time() - start)/60} min")


run()