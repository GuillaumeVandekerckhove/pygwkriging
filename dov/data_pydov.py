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

def main2():
    def internet():
        try:
            requests.get('https://www.google.com/').status_code
            return "Connected"
        except:
            return "Not Connected"


    def main():
        def connected():
            filter_elements = gwfilter.search(query=Join(df, 'pkey_filter'),
                                              return_fields=['pkey_filter', 'aquifer_code', 'diepte_onderkant_filter'])
            return filter_elements

        if internet() == "Connected":
            print("Connected to the internet.")
            filter_elements = gwfilter.search(query=Join(df, 'pkey_filter'),
                                              return_fields=['pkey_filter', 'aquifer_code', 'diepte_onderkant_filter'])
            return filter_elements

        else:
            print("waiting for internet connection")
            time.sleep(30)
            internet()
            while True:
                if internet() == "Not Connected":
                    print("waiting for internet connection")
                    time.sleep(30)
                    internet()
                elif internet() == "Connected":
                    print("Connected to the internet.")
                    connected()
                    break
        df['datum_monstername'] = df.to_datetime(df['datum_monstername'])

    print("We're going to define a starting and ending bounding box to get the data. This is to make sure that all the data is received.  ")
    minlowerleftx = 20000 #int(input('What is the minimum lower left value of x? '))#20000
    lowerlefty = 150000 #int(input('What is the lower left value of y? '))#150000
    minupperrightx = 25000 #int(input('What is the minimum upper right value of x? '))#25000
    upperrighty = 250000 #int(input('What is the upper right value of y? '))#250000
    maxlowerleftx = 250000 #int(input('What is the maximum lower left value of x? '))#250000
    maxupperrightx = 260000 #int(input('What is the maximum upper right value of x? '))#260000
    parameter = input('What is the parameter? (Al, pH, Volumetrisch vochtgehalte, Vochtspanning, Ni, Cr, Kalkgehalte, Fe, T, Cu, Glauconiet totaal, K , S, Zn, Pb, Fluor, As, Cd, Hg, Eh°, Na, Mg, NH4, Ca, Mn, Cl, SO4, HCO3, CO3, NO3, NO2, PO4, Sb, Co, Ag, Au, Ba, Be, B, Mo, Tha, Ti, V, Br, CN, CO2, Se, SiO2, F, Fe(Tot.), Fe2+, Fe3+, P, NaCl, H(tot), Si, N-totaal, P-totaal, PO4(Tot.), Sr, Sn, ...) ')

    fields = gwmonster.get_fields()
    print(fields['parameter'])

    dx = minupperrightx-minlowerleftx
    x = []
    x.extend([minlowerleftx])

    for i in x:
        if i < maxlowerleftx+dx:
            x2 = i + dx
            x.extend([x2])


    count = 0
    length = len(x)

    for i in x:
        logger.info(f"Asking data for bounding box : {i}, {lowerlefty}, {i+dx}, {upperrighty}, {count}/{length-1}")
        df = gwmonster.search(location=Within(Box(i, lowerlefty, i+dx, upperrighty)))
        df = df[df.parameter == parameter]
        df = pd.DataFrame(df)
        main()
        if i == x[0]:
            data = pd.merge(df, main())
        else:
            merge = pd.merge(df, main())
            data = data.append(merge)
        count = count + 1

    inputdata = jp(outputfile, "Inputdata.txt")


    data.to_csv(inputdata, header=False,index=True,sep='\t', mode='a')


    inputtxtfile = jp(outputfile, "Input.txt")
    list1 = []
    list1.extend(['inputfile ' + inputdata] + ['hcov 18'] + ['datum 11'] + ['permkey 5'] + ['parameter 15'] + ['x 7'] + ['y 8'] + ['z 19'] + ['index 0'] + ['maps no'])

    np.savetxt(inputtxtfile, list1, delimiter="\n", fmt="%s")
    return inputtxtfile

