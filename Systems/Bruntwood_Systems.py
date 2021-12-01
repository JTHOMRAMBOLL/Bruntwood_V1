# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 15:48:29 2021

@author: JTHOM
"""
import pandas as pd

class System():
    
# A class to defin the systems which will be used on Bruntwood 
    def __init__(self,System_Ref,Name,Eff_Type,Cost,Capacity, Lifespan,Description,**Efficency):
        
        self.System_Ref=System_Ref
        self.Name=Name
        self.Eff_Type=Eff_Type
        self.Efficency = Efficency
        self.Cost=Cost
        self.Capacity=Capacity
        self.Lifespan= Lifespan
        self.Description=Description
        
    def System_Type(self):
        print(self.Efficency.values())
        
        if self.Eff_Type=='COP':
            
            Eff_Out=[1/i for i in self.Efficency.values()]
            
        elif self.Eff_Type=='%':
            
            Eff_Out=[1/i for i in self.Efficency.Values()]
            
        return(Eff_Out)

class SystemPD():
    
# A class to defin the systems which will be used on Bruntwood 
    def __init__(self,System_Ref,Name,System_Type,System_Fuel, Lifespan,Cost,Capacity,Eff_Type,Description,Efficency):
        
        self.System_Ref=System_Ref
        self.Name=Name
        self.System_Type=System_Type
        self.System_Fuel=System_Fuel
        self.Eff_Type=Eff_Type
        self.Efficency = Efficency
        self.Cost=Cost
        self.Capacity=Capacity
        self.Lifespan= Lifespan
        self.Description=Description
        self.SFP=1
        self.HRU=1
        self.Eff_Out=1
    #Function to pull headline Eff/SFP/HRU from supply side intervention    
    def Vent_Eff_Cal(self):

        SPF_Out=self.SFP
        HRU_Out=self.HRU
        EFF_Out=self.Eff_Out     
            
        if self.Eff_Type=='COP':
            
            EFF_Out=1/self.Efficency.mean(axis = 0)        
            
        elif self.Eff_Type=='%':
            
            EFF_Out=self.Eff_Out=self.Efficency.mean(axis = 0)
        
        elif self.Eff_Type=='SFP':            
            
            
            SPF_Out=self.Efficency['SFP'].mean(axis = 0)
            HRU_Out=self.Efficency['HRU'].mean(axis = 0)
           
        Eff_Metrics={'SPF':SPF_Out,'HRU':HRU_Out,'EFF':EFF_Out}
            
        return(Eff_Metrics)
    
    def Renew(self,PV_Area,BuildingArea):
       # EFF_Out=self.Eff_Out
        Elec_Yeild_Out='N/A'
        DHW_Yeild_Out='N/A'
        
        if self.System_Type=='Renewable':
            Elec_Yeild_Out=self.Efficency['Electrical Yeild']*PV_Area/BuildingArea
            DHW_Yeild_Out=self.Efficency['DHW Yeild']*PV_Area/BuildingArea
            #EFF_Out=self.Efficency['Efficency']
        Renew_Metrics={'PV Yeild':Elec_Yeild_Out.values[0],'PT Yeild':DHW_Yeild_Out.values[0]}
        return(Renew_Metrics)

    def HC_Eff(self):
          
        if self.Eff_Type=='COP':
            #print('Hello=',self.Name)
           
            HTG_Out=(1/self.Efficency['Htg Efficency']).mean(axis = 0) 
            CLG_Out=(1/self.Efficency['Clg Efficiency']).mean(axis = 0) 
        
        elif self.Eff_Type=='%':
            
            HTG_Out=self.Efficency['Htg Efficency'].mean(axis = 0) 
            CLG_Out=self.Efficency['Clg Efficiency'].mean(axis = 0) 
        
        Renew_Metrics={'HTG_Eff':HTG_Out,'CLG_Eff':CLG_Out}    
        return(Renew_Metrics)
    
  
    def Mean_Eff(self):
          
        if self.Eff_Type=='COP':
            
            Eff_Out=1/self.Efficency
            
        elif self.Eff_Type=='%':
            if self.System_Type=='Lighting' or self.System_Type=='Lighting Control' or self.System_Type=='PlugLoads':
                Eff_Out=self.Efficency
            else:
                Eff_Out=(1-self.Efficency)+1
        
        Mean_Eff_Out=Eff_Out.mean(axis = 0) 

        return(Mean_Eff_Out[0])
    
def Get_Systems(FilePath):
   
    Systems_Data=pd.read_excel(FilePath)
    Systems_Data=Systems_Data.set_index(Systems_Data['System Ref'])
    Systems=[SystemPD(Systems_Data['System Ref'].loc[i],Systems_Data['System Name'].loc[i],Systems_Data['Type'].loc[i],Systems_Data['Fuel'].loc[i],
                  Systems_Data['Life Span'].loc[i],Systems_Data['Cost Indication'].loc[i],Systems_Data['Capacity'].loc[i],
                  Systems_Data['Efficency Type'].loc[i],Systems_Data['Description'].loc[i],
                  pd.read_excel(FilePath,sheet_name=Systems_Data['System Ref'].loc[i],index_col=0))                                                   
                  for i in Systems_Data['System Ref']]
    
    
    S_Names=[i.Name for i in Systems]
    Sys_Out=dict(zip(S_Names,Systems))
    
    return(Sys_Out,S_Names)


def Filter_INT(SS_Ints,SearchTerm):
    
    SS_Type=SS_Ints.values()
    Filter_Type = [n for n in SS_Type if n.System_Type == SearchTerm]
    
    return(Filter_Type)


FP_Supply_Side_Int=FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\ST_James\\SJB_PC_WP2_SystemsV1.xlsx'
SS_INTS=Get_Systems(FP_Supply_Side_Int)
print(SS_INTS[0])
Test=Filter_INT(SS_INTS[0],'Heating&Cooling')[0].Mean_Eff()
print(Test)

