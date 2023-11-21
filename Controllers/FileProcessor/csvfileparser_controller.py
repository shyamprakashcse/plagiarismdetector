import pandas as pd   
import numpy as np 
from Controllers.AWS import aws_controller
df = pd.read_csv('./GE23FTF.csv') 

json_list = df.to_dict(orient='records') 
intern_data = {} 
for record in json_list: 
    del record['Unnamed: 0'] 
    record['Intern_ID'] = str(record['Intern_ID']).strip() 
    record['Batch_No'] = str(record['Batch_No']).strip()  
    intern_data[record['Intern_ID']]= record 
    

print("Intern Data Fetched...") 
# aws_controller.updateItemInDynamoDB('Plagiarism-Detector',{'Intern_ID':'901135'},{'Status':"Testing"})


