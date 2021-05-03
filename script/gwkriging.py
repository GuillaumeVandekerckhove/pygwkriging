import os
import glob
import time
import shutil
from os.path import join as jp
from pysgems.algo.sgalgo import XML
from pysgems.dis.sgdis import Discretize
from pysgems.io.sgio import PointSet
from pysgems.plot.sgplots import Plots
from pysgems.sgems import sg
#from pysgems.variogram import space_to_tab
#from pysgems.variogram import variogram_total
#from pysgems.gslib import gslib
from loguru import logger

files = []

os.mkdir("programrun")
os.mkdir("QGiS")
output = os.getcwd()
output1 = jp(output, "programrun")

list2 = []
def pydov(pydovdata):

    list2.extend([pydovdata])
    if pydovdata == 'yes':
        #import dov.data_pydov as datapydov
        #datapydov.main2()
        output2 = output.strip('script')
        inputtxtfile = jp(output, 'Input.txt')
        spacetotab(inputtxtfile,2)
        inputtxtfile = inputtxtfile + 'spacetotabs' + 'no_whiterules.txt'
        outputtxtfile = jp(output2, 'datafilter', 'Input.txt')
        shutil.move(inputtxtfile, outputtxtfile)

    else:
        None

def filterdata(datafile, pydovdata):
    import datafilter.dataset_filter as data
    data.main(datafile,pydovdata)


def spacetotab(i, columns):
    import pysgemsAdd.space_to_tab as tab
    tab.main(i, columns)
    #space_to_tab.main(i)


list1 = []


def getsgemsfiles():
    outputfile = os.getcwd()
    #outputfile = jp(outputfile, "filterdata_variogram_kriging")
    datafiles1 = glob.glob(outputfile + "/resultsdata2d//*.txt")

    def joinStrings(stringList):
        """Add strings together to get one string."""
        return ''.join(string for string in stringList)

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
    getsgemsfiles()
    import pysgemsAdd.variogram_total as variogram

    for i in list1:
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
        spacetotab(inputfile,4)
        inputfile = inputfile + 'spacetotabsno_whiterules.txt'
        variogram.main(inputfile, nbpoints)
        #variogram_total.main(inputfile, nbpoints)


def coordinates(inputfile, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input):
    import pysgemsAdd.gslib as gslib
    outputfolder = os.getcwd()
    outputfolder = jp(outputfolder, "QGiS")
    gslib.main(inputfile, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input, outputfolder)


def kriging(dataset):
    list2 = []
    # %% Initiate sgems pjt
    cwd = os.getcwd()  # Working directory
    #cwd = jp(cwd, "filterdata_variogram_kriging")
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
    print(pjt.point_set.columns)

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

    namekrigingvar = "results(var)"
    result_file_kriging_variance = jp(rdir, namekrigingvar + ".grid")
    save = "kriging_var"
    #pl.plot_2d(namekrigingvar, save=save)
    pl.plot_2d(res_file=result_file_kriging_variance, save=save)
    list2.extend([result_file_kriging_variance])

    for i in list2:
        coordinates(i, dx_input, dy_input, x0_input, y0_input, x_lim_input, y_lim_input)




def removefolder():
    move = input('Do you want to remove the temporary files and the definitive folders? ')
    if move == 'yes':
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
        files.extend([aquiferall] + [aquiferhead] + [resultsdata] + [resultsdata2d] + [year] + [inputfile2] + [inputfile3] + [inputfile4] + [resultsdata2d_sgems] + [qgis])

        for f in files:
            shutil.move(f, output1)
    else:
        None




def run():
    start = time.time()
    pydovdata = input('Do you want to work with pydov or not? (yes/no) ')
    pydov(pydovdata)
    for i in list2:
        filterdata(i,pydovdata)
    nbpoints = input('How many points do you want the variogram to display? ')
    nbpoints = int(nbpoints)
    variogram(nbpoints)
    for i in list1:
        kriging(i)
    logger.info(f"ran the full algorithm in {time.time() - start} s or {(time.time() - start)/60} min")

    removefolder()
run()