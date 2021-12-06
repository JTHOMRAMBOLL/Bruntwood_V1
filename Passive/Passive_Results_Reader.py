import pandas as pd
import os as os
import sqlite3
import matplotlib.pyplot as plt
import re
import time
import numpy 
try:
    from ladybug.sql import SQLiteResult
    from ladybug.datacollection import HourlyContinuousCollection, \
        MonthlyCollection, DailyCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))
try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.loadbalance import LoadBalance
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    import ladybug.datatype
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))
try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))



def subtract_loss_from_gain(gain_load, loss_load):
    """Create a single DataCollection from gains and losses."""
    total_loads = []
    for gain, loss in zip(gain_load, loss_load):
        total_load = gain - loss
        total_load.header.metadata['type'] = \
            total_load.header.metadata['type'].replace('Gain ', '')
        total_loads.append(total_load)
    return total_loads


def serialize_data(data_dicts):
    """Reserialize a list of collection dictionaries."""
    if len(data_dicts) == 0:
        return []
    elif data_dicts[0]['type'] == 'HourlyContinuousCollection':
        return [HourlyContinuousCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'MonthlyCollection':
        return [MonthlyCollection.from_dict(data) for data in data_dicts]
    elif data_dicts[0]['type'] == 'DailyCollection':
        return [DailyCollection.from_dict(data) for data in data_dicts]

def pos(col): 
  return col[col > 0].sum()
  
def neg(col): 
  return col[col < 0].sum()

# List of all the output strings that will be requested
cooling_outputs = LoadBalance.COOLING + (
    'Cooling Coil Electricity Energy',
    'Chiller Electricity Energy',
    'Zone VRF Air Terminal Cooling Electricity Energy',
    'VRF Heat Pump Cooling Electricity Energy',
    'Chiller Heater System Cooling Electricity Energy',
    'District Cooling Chilled Water Energy',
    'Evaporative Cooler Electricity Energy')
heating_outputs = LoadBalance.HEATING + (
    'Boiler NaturalGas Energy',
    'Heating Coil Total Heating Energy',
    'Heating Coil NaturalGas Energy',
    'Heating Coil Electricity Energy',
    'Humidifier Electricity Energy',
    'Zone VRF Air Terminal Heating Electricity Energy',
    'VRF Heat Pump Heating Electricity Energy',
    'VRF Heat Pump Defrost Electricity Energy',
    'VRF Heat Pump Crankcase Heater Electricity Energy',
    'Chiller Heater System Heating Electricity Energy',
    'District Heating Hot Water Energy',
    'Baseboard Electricity Energy',
    'Hot_Water_Loop_Central_Air_Source_Heat_Pump Electricity Consumption',
    'Boiler Electricity Energy',
    'Water Heater NaturalGas Energy',
    'Water Heater Electricity Energy',
    'Cooling Coil Water Heating Electricity Energy')
lighting_outputs = LoadBalance.LIGHTING
electric_equip_outputs = LoadBalance.ELECTRIC_EQUIP
gas_equip_outputs = LoadBalance.GAS_EQUIP
process_outputs = LoadBalance.PROCESS
shw_outputs = ('Water Use Equipment Heating Energy',) + LoadBalance.HOT_WATER
fan_electric_outputs = (
    'Zone Ventilation Fan Electricity Energy',
    'Fan Electricity Energy',
    'Cooling Tower Fan Electricity Energy')
pump_electric_outputs = 'Pump Electricity Energy'
people_gain_outputs = LoadBalance.PEOPLE_GAIN
solar_gain_outputs = LoadBalance.SOLAR_GAIN
infil_gain_outputs = LoadBalance.INFIL_GAIN
infil_loss_outputs = LoadBalance.INFIL_LOSS
vent_loss_outputs = LoadBalance.VENT_LOSS
vent_gain_outputs = LoadBalance.VENT_GAIN
nat_vent_gain_outputs = LoadBalance.NAT_VENT_GAIN
nat_vent_loss_outputs = LoadBalance.NAT_VENT_LOSS

Fresh_Air="Zone Infiltration Current Density Volume Flow Rate"
Mechanical_Vent="Zone Mechanical Ventilation Mass Flow Rate"

all_output = \
[cooling_outputs, heating_outputs, lighting_outputs, electric_equip_outputs, gas_equip_outputs,
 process_outputs, shw_outputs, fan_electric_outputs, pump_electric_outputs,
 people_gain_outputs, solar_gain_outputs, infil_gain_outputs, infil_loss_outputs,
 vent_loss_outputs, vent_gain_outputs, nat_vent_gain_outputs, nat_vent_loss_outputs]

_sql=r'C:\Users\JTHOM\OneDrive - Ramboll\Documents\Dump\Sql\de66f1cf\outputs\sql\eplusout.sql'

def get_SQL(sql_FP):

    #assert os.path.isfile(_sql), 'No sql file found at: {}.'.format(_sql)
    assert os.path.isfile(sql_FP), 'No sql file found at: {}.'.format(_sql)
    # small file on windows; use IronPython like usual
    # create the SQL result parsing object
    sql_obj = SQLiteResult(sql_FP)

    # get all of the results relevant for energy use
    cooling = sql_obj.data_collections_by_output_name(cooling_outputs)
    heating = sql_obj.data_collections_by_output_name(heating_outputs)
    lighting = sql_obj.data_collections_by_output_name(lighting_outputs)
    electric_equip = sql_obj.data_collections_by_output_name(electric_equip_outputs)
    hot_water = sql_obj.data_collections_by_output_name(shw_outputs)
    
    vent_masss_flow= sql_obj.data_collections_by_output_name(Mechanical_Vent)
    #fresh_air_Flow= sql_obj.data_collections_by_output_name(Fresh_Air)
    
    infil_gain = sql_obj.data_collections_by_output_name(infil_gain_outputs)
    infil_loss = sql_obj.data_collections_by_output_name(infil_loss_outputs)
    vent_loss = sql_obj.data_collections_by_output_name(vent_loss_outputs)
    vent_gain = sql_obj.data_collections_by_output_name(vent_gain_outputs)
    
    
        # do arithmetic with any of the gain/loss data collections
    if len(infil_gain) == len(infil_loss):
        infiltration_load = subtract_loss_from_gain(infil_gain, infil_loss)
    if len(vent_gain) == len(vent_loss) == len(cooling) == len(heating):
        mech_vent_loss = subtract_loss_from_gain(heating, vent_loss)
        mech_vent_gain = subtract_loss_from_gain(cooling, vent_gain)
        mech_vent_load = [data.duplicate() for data in
                          subtract_loss_from_gain(mech_vent_gain, mech_vent_loss)]
        for load in mech_vent_load:
            load.header.metadata['type'] = \
                'Zone Ideal Loads Ventilation Heat Energy'
    
    
    Results_Dict={"out:Annual Heat":heating,"out:Annual Cool":cooling,"out:Annual Lighting":lighting,"out:Annual Elec equipt":electric_equip,
                  "out:Annual DHW":hot_water,"out:Annual Mech Ventilation":vent_masss_flow,'out: Infiltration Load':infiltration_load,
                  "out:Mech Vent Load":mech_vent_load}
    return(Results_Dict)





def sql_Data(_data,type_):
    
    operator = '+'
    statement = 'data {} data_i'.format(operator)

    # perform the arithmetic operation
    data = _data[0]
    for data_i in _data[1:]:
        data = eval(statement, {'data': data, 'data_i': data_i})  # I love Python!

    # try to replace the data collection type
    try:
        data = data.duplicate()
        if type_:
            data.header.metadata['type'] = type_
        elif 'type' in data.header.metadata:
            d_unit = data.header.unit
            for key in ladybug.datatype.UNITS:
                if d_unit in ladybug.datatype.UNITS[key]:
                    base_type = ladybug.datatype.TYPESDICT[key]()
                    data.header.metadata['type'] = str(base_type)
                    break
            else:
                data.header.metadata['type'] = 'Unknown Data Type'
        if 'System' in data.header.metadata:
            data.header.metadata.pop('System')
        if 'Zone' in data.header.metadata:
            data.header.metadata.pop('Zone')
    except AttributeError:
        pass  # data was not a data collection; just return it anyway
    
    
    
    return(list(data.values))




def Results_PP(Results_Dict,Name):
    t1=time.time()
    Results=[sql_Data(k,v) for k,v in zip(Results_Dict.values(),Results_Dict.keys())]
    DF=pd.DataFrame(Results,index=Results_Dict.keys()).T
    Index=pd.date_range(start='1/1/2021', periods=8760, freq='h')
    DF=DF.set_index(Index)
    
    
    
    
    Summed_Totals=DF.sum()
    Summed_Totals['out:Name']=Name
    
    #Fresh air load pre processing 
    Summed_Totals["out:FA Cooling Load"]=DF["out:Mech Vent Load"].agg([pos])['pos']
    Summed_Totals["out:FA Heating Load"]=DF["out:Mech Vent Load"].agg([neg])['neg']
    Summed_Totals["out:FA Total Load"]=(-1*Summed_Totals["out:FA Heating Load"])+Summed_Totals["out:FA Cooling Load"]
    #Infiltration load pre processing 
    Summed_Totals["out:INF Cooling Load"]=DF['out: Infiltration Load'].agg([pos])['pos']
    Summed_Totals["out:INF Heating Load"]=DF['out: Infiltration Load'].agg([neg])['neg']
    Summed_Totals["out:INF Total Load"]=(-1*Summed_Totals["out:INF Heating Load"])+Summed_Totals["out:INF Cooling Load"]
    
    print(Summed_Totals)
    
    #Summed_Totals["out:FA Cooling Load"]=Temp["out:FA Cooling Load"]
    #Summed_Totals["out:FA Heating Load"]=Temp["out:FA Heating Load"]
    Dict=Summed_Totals.to_dict()
    t2=time.time()
    print(("It takes %s seconds to extract "+Name) % (t2 - t1))
    return(Dict)

def extract_name(Name):
    print(Name)
    Code=re.split("_",Name)[1]
    #print(Code)
    _Wall=Code[0]
    _Roof=Code[1]
    _Ground_Floor=Code[2]
    _Glazing=Code[3]
    _Rooflights=Code[4]
    _Airtightness=Code[5]
    Wall=[{'Name':'Wall.Basecase_'},
    {'Name':'Wall.Regs_'},
    {'Name':'Wall.Pilot_'}][int(_Wall)]
    Roof=[{'Name':'Roof.Basecase_'},
    {'Name':'Roof.Regs_'}][int(_Roof)]
    Floor=[{'Name':'Floor.Basecase_'},
    {'Name':'Floor.Regs_'}][int(_Ground_Floor)]
    Glazing=[{'Name':'Glazing.Basecase_'},
    {'Name':'Glazing.Regs_'},
    {'Name':'Glazing.Pilot_'}][int(_Glazing)]
    Rooflights=[{'Name':'Rooflights.Basecase_'},
    {'Name':'Rooflights.Regs_'},
    {'Name':'Rooflights.Pilot_'}][int(_Rooflights)]
    AirTightness=[{'Name':'AirTightness.Basecase'},
    {'Name':'Airtightness.Regs'},
    {'Name':'Airtightness.Pilot'}][int(_Airtightness)]

    Name=Name+"_"+Wall['Name']+Roof['Name']+Floor['Name']+Glazing['Name']+Rooflights['Name']+AirTightness['Name']
    #print(Name)
    return(Name)

def Results_Hourly(Results_Dict,Name):
    t1=time.time()
    Results=[sql_Data(k,v) for k,v in zip(Results_Dict.values(),Results_Dict.keys())]
    DF=pd.DataFrame(Results,index=Results_Dict.keys()).T
    Index=pd.date_range(start='1/1/2021', periods=8760, freq='h')
    DF=DF.set_index(Index)
    
    
    
    
    Summed_Totals=DF#.sum()
    Summed_Totals['out:Name']=Name
    
    #Fresh air load pre processing 
    Summed_Totals["out:FA Cooling Load"]=DF["out:Mech Vent Load"].agg([pos])['pos']
    Summed_Totals["out:FA Heating Load"]=DF["out:Mech Vent Load"].agg([neg])['neg']
    Summed_Totals["out:FA Total Load"]=(-1*Summed_Totals["out:FA Heating Load"])+Summed_Totals["out:FA Cooling Load"]
    #Infiltration load pre processing 
    Summed_Totals["out:INF Cooling Load"]=DF['out: Infiltration Load'].agg([pos])['pos']
    Summed_Totals["out:INF Heating Load"]=DF['out: Infiltration Load'].agg([neg])['neg']
    Summed_Totals["out:INF Total Load"]=(-1*Summed_Totals["out:INF Heating Load"])+Summed_Totals["out:INF Cooling Load"]
    
    print(Summed_Totals)
    
    #Summed_Totals["out:FA Cooling Load"]=Temp["out:FA Cooling Load"]
    #Summed_Totals["out:FA Heating Load"]=Temp["out:FA Heating Load"]
    ict=Summed_Totals.to_dict()
    t2=time.time()
    print(("It takes %s seconds to extract "+Name) % (t2 - t1))
    return(Summed_Totals)

    
    print(("It takes %s seconds to upload "+Reality_Name) % (t2 - t1))


#Please provide a filepath to the diretory file , which should contain the names and file paths of the sql results 
directory_fp=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\ST_James\\Directory.xlsx'

DF=pd.read_excel(directory_fp)
Names=DF['Name']
File_Paths=DF['File_Path']



#Please eneter a filepath for the location of the data output from the SQL files 
FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\ST_James\\data.xlsx'
#FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\Plaza\\data.xlsx'
#print([Name_in) for (Name_in) in zip(DF['Name'],DF['File_Path'])])


Batch_Download=pd.DataFrame([Results_PP(get_SQL(_sql),extract_name(Name_in)) for (Name_in,_sql) in zip(DF['Name'],DF['File_Path'])])
Batch_Download.to_excel(FP)

#_sql_FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\Plaza\\Plaza_000000\\116a9b0d\\outputs\\sql\\eplusout.sql'

"""
_sql_FP=r'C:\Users\JTHOM\OneDrive - Ramboll\Documents\Dump\Sql\Plaza\Plaza_000000\6d837694\outputs\sql\eplusout.sql"'
Annual=Results_Hourly(get_SQL(_sql_FP),'Results 2')
Annual.to_excel(FP)
"""




#fi1, ax1 = plt.subplots() 

#DF.plot(ax=ax1)
#fi2, ax2 = plt.subplots() 

#Summed_Totals.plot.bar(ax=ax2)
#plt.show()



