import os
import json
import zipfile
import pathlib
from pandas import DataFrame
from pollination_streamlit.selectors import job_selector
from pollination_streamlit.interactors import Job
from ladybug.sql import SQLiteResult
import pandas as pd



defult_url ='https://app.pollination.cloud/projects/jamesthomson/st-james/jobs/' \
'57b120e6-0e92-4ccd-b290-464769b02f7f'
api_key='ECA6D3DC.51B149B0BB54DF2120624C14'


try:
    job = job_selector(
        api_key=api_key,
        default=defult_url
    )
except Exception:
    print(
        'The app cannot access this job on Pollination. Ensure the url is '
        'correct. In case the job is from a private project you will need to '
        'provide an API key to the app.\n\n :point_left: See the sidebar for '
        'more information.'
    )

def download_results(job: Job):
    """Download all of the SQL files associated with the results of a job."""
    df = job.runs_dataframe.dataframe
    job_id = job.id
    runs = job.runs
    results_folder = pathlib.Path('data', job_id)
    total_run = len(runs)
    print(total_run,results_folder)
    for count, (index, row) in enumerate(df.iterrows()):
        run = runs[count]
        run_folder = results_folder.joinpath(run.id)
        run_folder.mkdir(parents=True, exist_ok=True)
        print(run_folder)
        try:
            # download the sql output
            sql_zip = run.download_zipped_output('sql')
            with zipfile.ZipFile(sql_zip) as zip_folder:
                zip_folder.extractall(run_folder.as_posix())
        except :
             print(
                'Some of the runs of the job have failed.\n'
                'It may not be possible to scroll through all results.'
            )
    #print(run_folder)


def extract_user_inputs(job: Job):
    """Extract the various combinations of user inputs for a job."""
    # variables to be used while looping through the runs
    all_inputs = {}
    job_id = job.id
    results_folder = pathlib.Path('data', job_id).resolve()
    # loop through the runs and find all unique user inputs
    Directory={}
    #Directory['Simulation Name']=[i.status.inputs.value for i in job.runs if i.status.inputs.name=='_name_']
    Directory["File Path"]=[str(results_folder.joinpath(i.id).resolve())+'\\eplusout.sql' for i in job.runs]
    Directory["Job Path"]=[str(results_folder) for i in job.runs]
    print(Directory)
    inp_value = []
    for run in job.runs:
    
        for inp in run.status.inputs:
            
            if inp.name =='_name_' :
                
                try:
                    #print(inp.value)
                    Name=inp.value
                    #all_inputs[inp.name].add(inp.value)
                except KeyError:
                    print("na")
        inp_value.append(Name)          
        #print(inp_value)
    Directory['Simulation Name']=inp_value
    DF=pd.DataFrame.from_dict(Directory)
    FP=str(results_folder)+"\\Directory.xlsx"
    DF.to_excel(FP)
    print(FP)
    
    return  DF


#test= download_results(job) 
Get_Directory=extract_user_inputs(job)
print(Get_Directory)

