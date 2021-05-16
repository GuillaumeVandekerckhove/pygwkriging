import time
import pandas as pd
import requests
import pydov.search.grondwaterfilter
from pydov.search.grondwatermonster import GrondwaterMonsterSearch
from pydov.util.location import Within, Box
from pydov.util.query import Join
from loguru import logger
import os
from os.path import join as jp
import numpy as np


gwmonster = GrondwaterMonsterSearch()
gwfilter = pydov.search.grondwaterfilter.GrondwaterFilterSearch()
outputfile = os.getcwd()

# asking the coordinates of the starting and ending bounding box
print("We're going to define a starting and ending bounding box to get the data. This is to make sure that all the data is received.  ")
minlowerleftx = 20000  # int(input('What is the minimum lower left value of x? '))#20000
lowerlefty = 150000  # int(input('What is the lower left value of y? '))#150000
minupperrightx = 25000  # int(input('What is the minimum upper right value of x? '))#25000
upperrighty = 250000  # int(input('What is the upper right value of y? '))#250000
maxlowerleftx = 250000  # int(input('What is the maximum lower left value of x? '))#250000
maxupperrightx = 260000  # int(input('What is the maximum upper right value of x? '))#260000
# asking from which parameter the data has to be downloaded
parameter = input('What is the parameter? (Al, pH, Volumetrisch vochtgehalte, Vochtspanning, Ni, Cr, Kalkgehalte, Fe, T, Cu, Glauconiet totaal, K , S, Zn, Pb, Fluor, As, Cd, Hg, Eh°, Na, Mg, NH4, Ca, Mn, Cl, SO4, HCO3, CO3, NO3, NO2, PO4, Sb, Co, Ag, Au, Ba, Be, B, Mo, Tha, Ti, V, Br, CN, CO2, Se, SiO2, F, Fe(Tot.), Fe2+, Fe3+, P, NaCl, H(tot), Si, N-totaal, P-totaal, PO4(Tot.), Sr, Sn, ...) ')


def internet():
    """ Function to check the internet connection."""
    try:
        requests.get('https://www.google.com/').status_code
        logger.info(f"Connected to the internet.")
        return "Connected"
    except:
        logger.info(f"Not connected to the internet.")
        return "Not Connected"


def connected(i, length, minlowerleftx, lowerlefty, upperrighty, parameter, dx, count):
    """ Function to get the groundwater data. """

    logger.info(f"Asking data for bounding box : {i}, {lowerlefty}, {i + dx}, {upperrighty}, {count}/{length - 1}")  # print info for the user, from which bounding box the data is downloading
    logger.info(f"Asking data for groundwater monsters.")
    df = gwmonster.search(location=Within(Box(i, lowerlefty, i + dx, upperrighty)))  # downloading the data for the groundwater monsters
    df = df[df.parameter == parameter]
    df = pd.DataFrame(df)
    logger.info(f"Connecting the groundwater filters.")
    filter_elements = gwfilter.search(query=Join(df, 'pkey_filter'),return_fields=['pkey_filter', 'aquifer_code', 'diepte_onderkant_filter'])
    df['datum_monstername'] = pd.to_datetime(df['datum_monstername'])
    data = pd.merge(df, filter_elements)
    return data


def main():
    # creating the coordinates for the different bounding boxes, so the bounding box is small enough that there are no more than 10000 data points in one bounding box (otherwise error from pydov)
    dx = minupperrightx - minlowerleftx
    x = []
    x.extend([minlowerleftx])
    for i in x:
        if i < maxlowerleftx + dx:
            x2 = i + dx
            x.extend([x2])
    length = len(x)
    count = 0
    # downloading all the data per bounding box
    for i in x:
        if internet() == "Connected":
            if i == minlowerleftx:
                data = connected(i, length, minlowerleftx, lowerlefty, upperrighty, parameter, dx, count)
            else:
                merge = connected(i, length, minlowerleftx, lowerlefty, upperrighty, parameter, dx, count)
                data = data.append(merge)
            logger.info(f"# Rows of data = {len(data.index)}")
            count = count + 1
        else:
            # if there is no internet connection, the program waits 30 seconds and then retries
            print("waiting for internet connection")
            time.sleep(30)
            internet()
            while True:
                if internet() == "Not Connected":
                    print("waiting for internet connection")
                    time.sleep(30)
                    internet()
                elif internet() == "Connected":
                    if i == minlowerleftx:
                        data = connected(i, length, minlowerleftx, lowerlefty, upperrighty, parameter, dx, count)
                    else:
                        merge = connected(i, length, minlowerleftx, lowerlefty, upperrighty, parameter, dx, count)
                        data = data.append(merge)
                    logger.info(f"# Rows of data = {len(data.index)}")
                    count = count + 1
                    break
    # creating the inputdata file
    inputdata = jp(outputfile, "Inputdata.txt")
    data.to_csv(inputdata, header=False, index=True, sep='\t', mode='a')
    # creating the file that contains the input parameters needed for the program
    inputtxtfile = jp(outputfile, "Input.txt")
    list1 = []
    list1.extend(['inputfile ' + inputdata] + ['hcov 18'] + ['datum 11'] + ['permkey 5'] + ['parameter 15'] + ['x 7'] + ['y 8'] + ['z 19'] + ['index 0'] + ['maps no'])
    np.savetxt(inputtxtfile, list1, delimiter="\n", fmt="%s")
    return inputtxtfile

def retry(max_tries=25):
    for i in range(max_tries):
        try:
           time.sleep(30)
           main()
           break
        except Exception:
            continue
