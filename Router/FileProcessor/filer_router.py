from fastapi import APIRouter, Request, status, Form, HTTPException 
from fastapi import FastAPI,Form,UploadFile,File,BackgroundTasks 
from Controllers.AWS import aws_controller 
from Controllers.FileProcessor import csvfileparser_controller
import io    
import zipfile
import os 
import shutil 

file_router = APIRouter(

    prefix='/file'

)

@file_router.post("/plagiarismformprocessor")
async def folderuploader(name:str=Form(),aidNumber:str=Form(),batchNumber:str=Form(),file:UploadFile=File()): 
    # print(name,aidNumber,batchNumber)  
    
    # Fetching the intern details and Validating intern ID and Batch No 
    interns_list = csvfileparser_controller.intern_data 
    if aidNumber not in interns_list:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Intern ID is not present") 
    else: 
        intern_record = interns_list[aidNumber] 
        if intern_record["Batch_No"]!=batchNumber.strip(): 
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=f"Invalid Batch No. You are not associated with that batch")
    
    
    try:
        # check whether it is a new upload 
        status_resp = aws_controller.getItemFromDynamoDB("Plagiarism_Detector",{"Intern_ID":aidNumber}) 
        if status_resp['code']==200 and status_resp["res"]["Upload_Status"] == True: 
            return {"code":400,"message":"We found that you have already uploaded a file"}
        zip_content = await file.read()

        # Create a BytesIO object to work with the ZIP content
        zip_buffer = io.BytesIO(zip_content)

        # Extract the contents of the ZIP file
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            # List the contents of the ZIP file
            file_list = zip_ref.namelist()
            root_folder = None
            subfolders = set() 
            # print(file_list) 
            
            for file_name in file_list:
                parts = file_name.split("/") 
                if "node_modules" in parts: 
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Please Upload without node_modules")
                    
                if len(parts) >= 1:
                    if root_folder is None:
                        root_folder = parts[0]
                    elif root_folder != parts[0]:
                        # If the root folder changes, consider it as a new root folder
                        root_folder = parts[0]

                if len(parts) >= 2:
                    subfolders.add(parts[1]) 
                    
                print(parts[-1])
            filenamewithoutext = os.path.splitext(file.filename)[0]
            if root_folder.strip()!=aidNumber.strip(): 
                return {"code":400,"message":"Invalid Folder Name Error Ocuurs.."}
                # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Folder Name. Folder Name should be your Intern ID") 
            elif len(subfolders)!=7: 
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Exactly 7 projects folders should be there . {len(subfolders)}  folders found") 
            
            UPLOAD_DIRECTORY = "INTERN_PORTAL_FY23/"
            # Create the upload directory if it doesn't exist
            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True) 
            
            print(file_list)
            
            # os.makedirs("INTERN_PORTAL_FY23/900999/Arun_vendorportal/",exist_ok=True)
            
            for file_name in file_list: 
                file_data = zip_ref.read(file_name)
                
                # Construct the file path in the upload directory 
                file_path = os.path.join(UPLOAD_DIRECTORY, file_name)
                # print(file_path)
                if file_path.endswith("/"): 
                    os.makedirs(file_path,exist_ok=True) 
                else: 
                    with open(file_path,'wb') as f: 
                        f.write(file_data)
                
        localfolderpath = f"/INTERN_PORTAL_FY23/{aidNumber}/"
        # print(localfolderpath) 
        
        # return "hellokkk"
        s3upload = aws_controller.upload_folder_to_s3(f"INTERN_PORTAL_FY23/{aidNumber}","plagiarism-detector",f"INTERN_PORTAL_FY23/{aidNumber}/") 
        if s3upload["code"] == 200:
            # Update the Status Field in DynamoDB 
            shutil.rmtree(f"INTERN_PORTAL_FY23/{aidNumber}/")
            print(f"Folder path deleted and its contents have been removed.")
            updateResp = aws_controller.updateItemInDynamoDB('Plagiarism_Detector',{"Intern_ID":aidNumber},{"Upload_Status":True}) 
            if updateResp["code"]==200:
                return {"code":200,"message":"Your Project folders has been uploaded Successfully and We tracked a status"} 
            else: 
                deleted_Resp = aws_controller.deleteFoldersInS3('plagiarism-detector',f'INTERN_PORTAL_FY23/{aidNumber}')
                return deleted_Resp 
        else: 
            shutil.rmtree(f"INTERN_PORTAL_FY23/{aidNumber}/")
            print(f"Folder path deleted and its contents have been removed.")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Exception arises while uploading into s3 due to "+s3upload["message"])
    
    
    except Exception as e: 
        # shutil.rmtree(f"INTERN_PORTAL_FY23/{aidNumber}/")
        # print(f"Folder path deleted and its contents have been removed.")
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail=repr(e))
        
    


