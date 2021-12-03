import pandas as pd
import re

FP=r'C:\Users\JTHOM\OneDrive - Ramboll\St James_Plaza NZC MEES Consultancy\Analysis\NZC Pathway Models\Plaza\Passive Data\data.xlsx'
DF=pd.read_excel(FP)

#for col in DF.columns:
#    print(col)

#print(DF['out:Name'])




def fab_name(Name):
    Code=re.split("_",Name)[2:]
    _Wall=re.split('Wall.',Code[0])[1]
    _Roof=re.split('Roof.',Code[1])[1]
    _Ground_Floor=re.split('Floor.',Code[2])[1]
    _Glazing=re.split('Glazing.',Code[3])[1]
    _Rooflights=re.split('Rooflights.',Code[4])[1]
    print(Code[5])
    _Airtightness=re.split('Airtightness.',Code[5])[1]
    Fab_dict={"Wall":_Wall,"Roof":_Roof,"Groud Floor":_Ground_Floor,"Glazing":_Glazing,"Rooflights":_Rooflights,"Airtightness":_Airtightness}
    print(Fab_dict)
    return(Fab_dict)

print(*DF['out:Name'].iloc[0])

test=[fab_name(i) for i in DF['out:Name']]