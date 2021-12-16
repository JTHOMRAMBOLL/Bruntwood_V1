# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 17:21:27 2021

@author: JTHOM
"""

# Libraries
import feather
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from Bruntwood_Systems import Get_Systems,Filter_INT
import PySimpleGUI as sg
from sqlalchemy import create_engine
import re
#engine = create_engine('sqlite:///C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\GitHub\\Bruntwood_V1\\data\\57b120e6-0e92-4ccd-b290-464769b02f7f\\results.sql', echo=False)
#################---------General Functions-------------################### 
def percentage_change(col1,col2):
    return ((col2 - col1) / col1) * 100

#This function calculates the energy required using Delta T and Volume in m3
def Vent_Eng(DryBulb,Air_Volume,Setpoint):        

    cp=1.0061
    density=1.202
    DeltaT=Setpoint-DryBulb
    #print(DeltaT)
    ExeriorEnergy=(Air_Volume/8760)*(density*cp)*DeltaT
    print(ExeriorEnergy)
    print((Air_Volume))
    Energy=ExeriorEnergy.sum(axis=0)#/GrossFloorArea
    return(Energy)


def Fan_Power(SFP,Air_Volume):
    Fan_Power=(SFP*(Air_Volume))
    
    return(Fan_Power)

def fab_name(Name):
    
    New_Name={'Basecase':'Existing','Regs':'NZC','Pilot':'NZC Enhanced'}
    
    
    Code=re.split("_",Name)[2:]
    _Wall=New_Name[re.split('Wall.',Code[0])[1]]
    _Roof=New_Name[re.split('Roof.',Code[1])[1]]
    _Ground_Floor=New_Name[re.split('Floor.',Code[2])[1]]
    _Glazing=New_Name[re.split('Glazing.',Code[3])[1]]
    _Rooflights=New_Name[re.split('Rooflights.',Code[4])[1]]
    _Airtightness=New_Name[re.split('Airtightness.',Code[5])[1]]
    Fab_dict={"Wall":_Wall,"Roof":_Roof,"Groud Floor":_Ground_Floor,"Glazing":_Glazing,"Rooflights":_Rooflights,"Airtightness":_Airtightness}
    return(Fab_dict)

plt.close('all')
############################-simulation data-###########


#Building Level Data 
#GrossFloorArea=14900.521257
GrossFloorArea=49172.839815#St_James
Building_FA_Volume=6.928416
Model_Mass_Flow=7.108677
#Floor_Area=1197.73# post process small power loads 
Baseline_SFP=1.6#To be confirmed 
#Fresh are split as per the calibration Model
FA_SPlit=0.75
AC_SPLIT=0.2


#Totals_FP=r'\\UKrammanfiler01\Projects\1620010755\05-Analysis\Sustainability Solutions\BEAR\Results\210617_Complex\data.xlsx'

Totals_FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\St James_Plaza NZC MEES Consultancy\\Analysis\\NZC Pathway Models\\Plaza\\Passive Data\\data.xlsx'
Weather_FP=r'C:\Users\JTHOM\OneDrive - Ramboll\St James_Plaza NZC MEES Consultancy\Analysis\NZC Pathway Models\Python\Fresh_air_reserc_check_Data.xlsx'

#Main Data impoirt of the Demand side scenarios
Totals_Data=pd.read_excel(Totals_FP)#.dropna().drop_duplicates(keep='first')
Weather_Data=pd.read_excel(Weather_FP,index_col=0)#.dropna().drop_duplicates(keep='first')
#print(Weather_Data)


#Set index to unique name and rename coloumns for display purposes 
Totals_Data=Totals_Data.set_index(Totals_Data['out:Name'])
#Totals_Data=Totals_Data/GrossFloorArea

Total_Plot=Totals_Data.filter(['out:Annual Heat','out:FA Heating Load','out:Annual Cool','out:Annual Lighting','out:Annual Elec equipt','out:Annual DHW','out:Annual Mech Ventilation','out: Fresh Air Flow Rate'],axis=1)
Total_Plot['Total Energy (kwh/m2)']=Total_Plot.sum(axis=1)
Total_Plot.rename(columns = {'out:Annual Heat':'Annual Heating Load (kWh/m2)','out:FA Heating Load':'Annual Fresh Air Load (kWh/m2)', 'out:Annual Cool':'Annual Cooling Load (kWh/m2)', 
                             'out:Annual Lighting':'Annual Lighting Load (kWh/m2)','out:Annual Elec equipt':'Annual Equipment Load (kWh/m2)',
                             'out:Annual DHW':'Annual DHW Load (kWh/m2)'},inplace=True)

Demand_Scenarios=range(Total_Plot.shape[0])
print(Demand_Scenarios)
print("Demand Scenario length= " +str(Total_Plot.shape[0]))



#Sorting preferences 
#Total_Plot=Total_Plot.sort_values(by=['Total Energy (kwh/m2)'], ascending=[True])
#Total_Plot=Total_Plot.sort_values(by=['Annual Heating Load (kWh/m2)'], ascending=[True])
Total_Plot=Total_Plot/GrossFloorArea

#Post Process the Small Power 
#Total_Plot['Annual Small Power load (kWh/m2)']= 8572 /Floor_Area

Total_Plot['Total Fresh Air Energy']=(Total_Plot['Annual Heating Load (kWh/m2)']*FA_SPlit)*(1-AC_SPLIT)

Q=Total_Plot['Total Fresh Air Energy'].iloc[0]

Mass_Flow=Total_Plot['out:Annual Mech Ventilation'].iloc[0]

#'Energy to temper air to 12.9
Q1=Mass_Flow*1.0061*1.202*(12.9+5)
print(Q1)

#Reduce air volume to represent recirculated volume
Mass_Flow_RC=Mass_Flow*0.5
T_Mix=((21*Mass_Flow_RC)+(-5*(Mass_Flow-Mass_Flow_RC)))/Mass_Flow
print(T_Mix)

Q2=Mass_Flow*1.0061*1.202*(12.9+(5-T_Mix))
#New inlet temperature when mexed with room air
print('Q2=',Q2,"percentage%",(Q1-Q2)/Q1)

6