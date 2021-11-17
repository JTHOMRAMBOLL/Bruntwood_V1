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
        
    def Eff_Cal(self):
        print(self.Efficency)
        
        if self.Eff_Type=='COP':
            
            Eff_Out=1/self.Efficency
            
        elif self.Eff_Type=='%':
            
            Eff_Out=self.Efficency
            
        return(Eff_Out)
    
    def Mean_Eff(self):
        print(self.Efficency)
          
        if self.Eff_Type=='COP':
            
            Eff_Out=1/self.Efficency
            
        elif self.Eff_Type=='%':
            
            Eff_Out=self.Efficency
                
        
        Mean_Eff_Out=Eff_Out.mean(axis = 0) 
            
        return(Mean_Eff_Out)
    
    

class System_Eff():
    
    def __init__(self,**kwargs):
        
        self.kwargs=kwargs
        #print(kwargs)
        
    def Values_Only(self):
        
        Values=self.kwargs.values()
        #print(Values)
        return(Values)



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



FP=r'\\UKrammanfiler01\Projects\1620010755\05-Analysis\Sustainability Solutions\BEAR\Python\Supply Side\Reference_Info\WP2_Systems.xlsx'
Test=Get_Systems(FP)

print(Test[1])



