import pandas as pd
import numpy as np
from openpyxl import load_workbook


path=r'C:\Users\JTHOM\OneDrive - Ramboll\General - Deputy Head of Digital Engineering\Bids\BAS WP E&F\220404BAS_SystemsV1 - Copy.xlsx'
path1=r'C:\Users\JTHOM\OneDrive - Ramboll\General - Deputy Head of Digital Engineering\Bids\BAS WP E&F\220404BAS_SystemsV1 - Copy - Copy.xlsx'

test=pd.read_excel(path, index_col=1,sheet_name="Master")
template=pd.read_excel(path, index_col=0,sheet_name="Template")
text=test['System Ref']

book = load_workbook(path1)
writer = pd.ExcelWriter(path1, engine = 'openpyxl')
writer.book = book




test=[template.to_excel(writer, sheet_name = str(i)) for i in text]
#df4.to_excel(writer, sheet_name = 'x4')
writer.save()
writer.close()