# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 17:21:27 2021

@author: JTHOM
"""

# Libraries
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from Bruntwood_Systems import Get_Systems#,Filter_INT



#################---------General Functions-------------################### 
def percentage_change(col1,col2):
    return ((col2 - col1) / col1) * 100

#This function calculates the energy required using Delta T and Volume in m3
def Vent_Eng(DryBulb,Air_Volume,Setpoint,FloorArea):        

    cp=1.0061
    density=1.202
    DeltaT=Setpoint-DryBulb
    #print(DeltaT)
    ExeriorEnergy=Air_Volume*(density*cp)*DeltaT
    #print(ExeriorEnergy)
    Energy=ExeriorEnergy.sum(axis=0)[0]/GrossFloorArea
    return(Energy)


def Fan_Power(SFP,Air_Volume,GrossFloorArea):
    Fan_Power=(SFP*(Air_Volume)*8670)/GrossFloorArea
    
    return(Fan_Power)



plt.close('all')
############################-simulation data-###########


#Building Level Data 
#GrossFloorArea=14900.521257
GrossFloorArea=15783.484657#model
Building_FA_Volume=6.928416
Model_Mass_Flow=7.108677
Floor_Area=1197.73
Baseline_SFP=1.6#To be confirmed 



Totals_FP=r'\\UKrammanfiler01\Projects\1620010755\05-Analysis\Sustainability Solutions\BEAR\Results\210617_Complex\data.xlsx'
Weather_FP=r'\\UKrammanfiler01\Projects\1620010755\05-Analysis\Sustainability Solutions\BEAR\Results\210617_Complex\Trafford_House_WeatherData.xlsx'


#Main Data impoirt of the Demand side scenarios
Totals_Data=pd.read_excel(Totals_FP)#.dropna().drop_duplicates(keep='first')
Weather_Data=pd.read_excel(Weather_FP,index_col=0)#.dropna().drop_duplicates(keep='first')



#Set index to unique name and rename coloumns for display purposes 
Totals_Data=Totals_Data.set_index(Totals_Data['out:Group'])
Total_Plot=Totals_Data.filter(['out:Annual Heat','out:Annual Cool','out:Annual Lighting','out:Annual Elec equipt','out:Annual DHW'],axis=1)
Total_Plot['Total Energy (kwh/m2)']=Total_Plot.sum(axis=1)
Total_Plot.rename(columns = {'out:Annual Heat':'Annual Heating Load (kWh/m2)', 'out:Annual Cool':'Annual Cooling Load (kWh/m2)', 
                             'out:Annual Lighting':'Annual Lighting Load (kWh/m2)','out:Annual Elec equipt':'Annual Equipment Load (kWh/m2)',
                             'out:Annual DHW':'Annual DHW Load (kWh/m2)'},inplace=True)

Demand_Scenarios=range(Total_Plot.shape[0])
print(Demand_Scenarios)
print("Demand Scenario length" +str(Total_Plot.shape[0]))



#Sorting preferences 
#Total_Plot=Total_Plot.sort_values(by=['Total Energy (kwh/m2)'], ascending=[True])
#Total_Plot=Total_Plot.sort_values(by=['Annual Heating Load (kWh/m2)'], ascending=[True])
Total_Plot=Total_Plot/GrossFloorArea

#Post Process the Small Power 
#Total_Plot['Annual Small Power load (kWh/m2)']= 8572 /Floor_Area


#Post Process the Freash Air Load 
Total_Plot['Annual Fresh Air Load (kWh/m2)']=Vent_Eng(Weather_Data,Building_FA_Volume,12.9,GrossFloorArea)

#Adjust Heating Load to suit
Total_Plot['Annual Heating Load (kWh/m2)']=Total_Plot['Annual Heating Load (kWh/m2)']-Total_Plot['Annual Fresh Air Load (kWh/m2)']

#Post Processed Fans Load 
Total_Plot['Annual Fan Power Load(kWh/m2)']=Fan_Power(Baseline_SFP,Model_Mass_Flow,GrossFloorArea)#This is a place holder for structure




#Example Steady state System Aplication 


#HtgEff,ClgEff,LghtEff,FanEff=[0.9,(1/4.5),(0.4*0.92),0.9]

Sys_Scenario={'Base':{'HtgEff':0.9,'ClgEff':(1/2),'LghtEff':1,'FanEff':1},
              'Dummy':{'HtgEff':(1/4.5),'ClgEff':(1/4.5),'LghtEff':(0.4*0.92),'FanEff':0.45}}
Current='Base'
#Current='Base'

#print(Sys_Scenario['Dummy'])


Total_Plot['Annual Heating Load (kWh/m2)']=Total_Plot['Annual Heating Load (kWh/m2)']*Sys_Scenario[Current]['HtgEff']
Total_Plot['Annual Cooling Load (kWh/m2)']=Total_Plot['Annual Cooling Load (kWh/m2)']*Sys_Scenario[Current]['ClgEff']
Total_Plot['Annual Lighting Load (kWh/m2)']=Total_Plot['Annual Lighting Load (kWh/m2)']*Sys_Scenario[Current]['LghtEff']
Total_Plot['Annual Equipment Load (kWh/m2)']=Total_Plot['Annual Equipment Load (kWh/m2)']*Sys_Scenario[Current]['FanEff']


#def Supply_Side_Int():

##############################################--------Supply Side Intervention Import ---------------------------##################################################

FP_Supply_Side_Int=FP=r'\\UKrammanfiler01\Projects\1620010755\05-Analysis\Sustainability Solutions\BEAR\Python\Supply Side\Reference_Info\WP2_SystemsV2.xlsx'
SS_INTS=Get_Systems(FP_Supply_Side_Int)



SS_Input_Demand=Total_Plot#.drop(['Total Energy (kwh/m2)'])

#Supply Side Interventions 
Heating=Filter_INT(SS_INTS[0],'Heating')
Cooling=Filter_INT(SS_INTS[0],'Cooling')


#This is the descirte list of supply side interventions 
#We need to combine the Heating and cooling
Heating_Cooling=Filter_INT(SS_INTS[0],'Heating&Cooling')+list(itertools.product(Heating,Cooling))


DHW_Master=Filter_INT(SS_INTS[0],'DHW')
Lighting=Filter_INT(SS_INTS[0],'Lighting')
Lighting_Cont=Filter_INT(SS_INTS[0],'Lighting Control')
EquipLoads=Filter_INT(SS_INTS[0],'PlugLoads')
Ventilation=Filter_INT(SS_INTS[0],'Ventilation') 
Renewables=Filter_INT(SS_INTS[0],'Renewable')

print(Renewables[1].Renew(80,GrossFloorArea))
print(len(Heating))
print(len(Cooling))
print('Descrete interventions')
print('INT_Heat_Cool',len(Heating_Cooling))
print('INT_DHW',len(DHW_Master))
print('INT_Light',len(Lighting))
print('INT_Light_CON',len(Lighting_Cont))
print('INT_Equip',len(EquipLoads))
print('INT_Vent',len(Ventilation))
print('INT_Renew',len(Renewables))

INT_Demand=Demand_Scenarios#[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
INT_Heat_Cool=[0,1,2,3,4]
INT_DHW=[0,1,2]
INT_Light=[0,1,2,3]
INT_Light_CON=[0,1,2]
INT_Plug=[0,1]
INT_Vent=[0,1,2,3,4]
INT_Renew=[0,1,2,3]

print(len(list(itertools.product(INT_Demand,INT_Heat_Cool,INT_DHW,INT_Light,INT_Light_CON,INT_Plug,INT_Vent,INT_Renew))))

def SH_Pre_Pocess(Heat_Cool):
  #This is a function to allow heating and cooling systems to be built from descrete systems or defined as a combined system   
    Data=0
    Name=0
    
    if isinstance(Heat_Cool,tuple):
        #print('Im a Tuple James')
        
        Htg_Eff=Heat_Cool[0].Mean_Eff()
        Cooling_Eff=Heat_Cool[1].Mean_Eff()      
               
        
        Htg_Ref=Heat_Cool[0].System_Ref       
        Cooling_Ref=Heat_Cool[1].System_Ref
        
        Htg_Name=Heat_Cool[0].Name        
        Cooling_Name=Heat_Cool[1].Name
        
        Name=Htg_Name+"_"+Cooling_Name    
        Ref=Htg_Ref+"_"+Cooling_Ref    
        Data={'HTG_Eff':Htg_Eff,'CLG_Eff':Cooling_Eff}
        
    elif isinstance(Heat_Cool,object):
        #print('Im a object James')
        
        Data=Heat_Cool.HC_Eff()
        Name=Heat_Cool.Name
        Ref=Heat_Cool.System_Ref 
        
    return{'Ref':Ref,'Name':Name,'Eff':Data}
        



   
def Supply_Side(Demand,SEL_Heat_Cool,SEL_DHW,SEL_Light,SEL_Light_CON,SEL_Equip,SEL_Vent,SEL_Renew):

    Perm_Demand=SS_Input_Demand.iloc[Demand]
    PV_Area=80
    BuildingArea=GrossFloorArea
    
    Heat_Cool=Heating_Cooling[SEL_Heat_Cool]
    DHW=DHW_Master[SEL_DHW]
    Light=Lighting[SEL_Light]
    Light_CON=Lighting_Cont[SEL_Light_CON]
    Equip=EquipLoads[SEL_Equip]
    Vent=Ventilation[SEL_Vent]
    Renew=Renewables[SEL_Renew]
    
    
    
    
    Perm_Heat_Cool=SH_Pre_Pocess(Heat_Cool)#Function gives Name and Eff
    
        
    Heating_Energy=Perm_Heat_Cool['Eff']['HTG_Eff']*Perm_Demand['Annual Heating Load (kWh/m2)']
    Cooling_Energy=Perm_Heat_Cool['Eff']['CLG_Eff']*Perm_Demand['Annual Cooling Load (kWh/m2)']
    
    
    
    
    Perm_DHW={'Ref':DHW.System_Ref,'Name':DHW.Name,'Eff':DHW.Mean_Eff()}
    
    DHW_Energy=Perm_DHW['Eff']*Perm_Demand['Annual DHW Load (kWh/m2)']
    
    
    Perm_Light={'Ref':Light.System_Ref,'Name':Light.Name,'Eff':Light.Mean_Eff()}   
    Perm_Light_CON={'Ref':Light_CON.System_Ref,'Name':Light_CON.Name,'Eff':Light_CON.Mean_Eff()}
    
    Lighting_Energy=Perm_Light['Eff']*Perm_Light_CON['Eff']*Perm_Demand['Annual Lighting Load (kWh/m2)']
    
    
    
   
    Perm_Equip={'Ref':Equip.System_Ref,'Name':Equip.Name,'Eff':Equip.Mean_Eff()}
    
    Equip_Energy=Perm_Equip['Eff']*Perm_Demand['Annual Equipment Load (kWh/m2)']
    
    
    
    
    Perm_Vent={'Ref':Vent.System_Ref,'Name':Vent.Name,'Eff':Vent.Vent_Eff_Cal()}
    Vent_Energy=Fan_Power(Perm_Vent['Eff']['SPF'],Model_Mass_Flow,GrossFloorArea)
    
    FA_Energy=Perm_Vent['Eff']['HRU']*Perm_Demand['Annual Fresh Air Load (kWh/m2)']
    
    
    

    Perm_Renew={'Ref':Renew.System_Ref,'Name':Renew.Name,'Yeild':Renew.Renew(PV_Area,BuildingArea)}
    
    PV_Energy=-Perm_Renew['Yeild']['PV Yeild']
    ST_Energy=-Perm_Renew['Yeild']['PT Yeild']
    #print(Perm_Vent['Eff']['HRU'])
    #print(Heating_Energy,Cooling_Energy,DHW_Energy,Lighting_Energy,Equip_Energy,Vent_Energy,FA_Energy,PV_Energy,ST_Energy)
    
    Store=[Perm_Heat_Cool,Perm_DHW,Perm_Light,Perm_Light_CON,Perm_Equip,Perm_Vent,Perm_Renew]
    Name=('.'.join([Perm_Demand.name]+[i['Ref'] for i in Store]))
    
    
    Total=sum([Heating_Energy,Cooling_Energy,Lighting_Energy,Equip_Energy,DHW_Energy,FA_Energy,Vent_Energy,PV_Energy,ST_Energy])

    Dict={'Permutation Name':Name,
      'Annual Heating Energy (kWh/m2) ':Heating_Energy,
      'Annual Cooling Energy (kWh/m2)':Cooling_Energy,
      'Annual Lighting Energy (kWh/m2)':Lighting_Energy,
      'Annual Equipment Energy (kWh/m2)':Equip_Energy,
      'Annual DHW Energy (kWh/m2)':DHW_Energy,
      'Annual Fresh Air Energy (kWh/m2)':FA_Energy,
      'Annual Fan Power Load(kWh/m2)':Vent_Energy,
      'Annual PV Energy (kWh/m2) ':PV_Energy,
      'Annual ST Energy (kWh/m2) ':ST_Energy,
      'Total Annual Energy (kWh/m2)':Total,
      'Fabric Intervention:':Perm_Demand.name,
      'Heating & Cooling Plant':Perm_Heat_Cool['Name'],
      'DHW':Perm_DHW['Name'],
      'Lighting':Perm_Light['Name'],
      'Lighting Control':Perm_Light_CON['Name'],
      'Lighting Equiptment':Perm_Equip['Name'],
      'Ventilation':Perm_Vent['Name'],
      'Renewables':Perm_Renew['Name'],
      }


       
    return(Dict)
test=Supply_Side(10,3,1,1,1,1,1,3)
print(test)
print(len(list(itertools.product(INT_Demand,INT_Heat_Cool,INT_DHW,INT_Light,INT_Light_CON,INT_Plug,INT_Vent,INT_Renew))))

##############################################-----------------------------------------------------------------##################################################

Results=[]
for x in (itertools.product(INT_Demand,INT_Heat_Cool,INT_DHW,INT_Light,INT_Light_CON,INT_Plug,INT_Vent,INT_Renew)):   
    DoIt=Supply_Side(x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7])
    Results.append(DoIt)
Results=pd.DataFrame(Results).set_index('Permutation Name')
   
print(Results.head())
print(Results.shape[0])



Results_FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\210618TrafordHouseResults.xlsx'
Results.to_excel(Results_FP,sheet_name='Results',header=True) 
   
##############################################-----------------------------------------------------------------##################################################