from fastapi import HTTPException,status
import requests 
from config import config 
import zipfile 
import io 
import os 

async def zipfileCustomRulesValidator(file,fields): 
    try: 
        zip_content = await file.read()
        # Create a BytesIO object to work with the ZIP content
        zip_buffer = io.BytesIO(zip_content) 
        
        # Extract the contents of the ZIP file
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            # List the contents of the ZIP file
            file_list = zip_ref.namelist()
            root_folder = None
            subfolders = set() 
            zip_ref.close()
            # print(file_list)   
            
        
        ## Write your conditions below   
        
        ## Getting a Root folder and sub folder 
        
        for file_name in file_list:
            parts = file_name.split("/") 
            if "node_modules" in parts: 
                return {"code":400,"message":"Please Upload without node_modules"} 
                    
            if len(parts) >= 1:
                if root_folder is None:
                    root_folder = parts[0]
                elif root_folder != parts[0]:
                    # If the root folder changes, consider it as a new root folder
                    root_folder = parts[0]

            if len(parts) >= 2:
                subfolders.add(parts[1])  
                
        # Root Folder Name Validation and Sub Folder Count Validation
        
        if root_folder.strip()!=fields["aidNumber"].strip(): 
            return {"code":400,"message": f"Exception Occurs due to Invalid Folder Name. Folder Name should be your Intern ID"}
            
        elif len(subfolders)<=2: 
            return {"code":400,"message":f"Exactly 7 projects folders should be there . {len(subfolders)}  folders found" } 
            
        else: 
            return {"code":200,"message":"Validation Successful"}
    except Exception as e: 
        return {"code":400,"message": f"Exception Occurs due to {repr(e)}"} 
    
    
async def zipFileUploader(file,localUploadPath): 
    try:
        zip_content = await file.read()

        # Create a BytesIO object to work with the ZIP content
        zip_buffer = io.BytesIO(zip_content)

        # Extract the contents of the ZIP file
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            # List the contents of the ZIP file
            file_list = zip_ref.namelist()
            
            
            
                 
            UPLOAD_DIRECTORY = "INTERN_PORTAL_FY23/"
            # Create the upload directory if it doesn't exist
            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True) 
            
            # print(file_list)
            
            # os.makedirs("INTERN_PORTAL_FY23/900999/Arun_vendorportal/",exist_ok=True)
            
            for file_name in file_list: 
                file_data = zip_ref.read(file_name)
                
                # Construct the file path in the upload directory 
                file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
                print(file_path)
                if file_path.endswith("/"): 
                    os.makedirs(file_path,exist_ok=True) 
                else: 
                    with open(file_path,'wb') as f: 
                        f.write(file_data)
                
        return {"code":200,"message":"Uploaded Successfully"}
                
    except Exception as e: 
        return {"code":400,"message":f"Exception occurs due to {repr(e)}"}
        
    



    

