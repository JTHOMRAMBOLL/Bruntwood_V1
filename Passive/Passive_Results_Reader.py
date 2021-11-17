import pandas as pd
import os as os
import sqlite3
import matplotlib.pyplot as plt
import re
import time

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

    Results_Dict={"out:Annual Heat":heating,"out:Annual Cool":cooling,"out:Annual Lighting":lighting,"out:Annual Elec equipt":electric_equip,"out:Annual DHW":hot_water}
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



   
    
    print(("It takes %s seconds to upload "+Reality_Name) % (t2 - t1))



directory_fp=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\ST_James\\Directory.xlsx'
DF=pd.read_excel(directory_fp)
Names=DF['Name']
File_Paths=DF['File_Path']

FP=r'C:\\Users\\JTHOM\\OneDrive - Ramboll\\Documents\\Dump\\Sql\\ST_James\\data.xlsx'

#print([Name_in) for (Name_in) in zip(DF['Name'],DF['File_Path'])])

test=pd.DataFrame([Results_PP(get_SQL(_sql),extract_name(Name_in)) for (Name_in,_sql) in zip(DF['Name'],DF['File_Path'])])
test.to_excel(FP)
print(test)


#test to see if github is working?




#fi1, ax1 = plt.subplots() 

#DF.plot(ax=ax1)
#fi2, ax2 = plt.subplots() 

#Summed_Totals.plot.bar(ax=ax2)
#plt.show()



