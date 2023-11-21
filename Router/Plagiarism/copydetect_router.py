from fastapi import APIRouter, Request, status, Form, HTTPException 
from Controllers.AWS import aws_controller
copydetect_router = APIRouter(

    prefix='/copydetector'

)

@copydetect_router.get("/getplagiarismreporttable")
def plagiarismReportTable(): 
    try:
        resp = aws_controller.GSIQueryingOnDynamoDB('Plagiarism_Detector','Report_Status-index','Report_Status',"True","==")
        if resp['ResponseMetadata']['HTTPStatusCode'] == 200: 
            if len(resp['Items'])!=0: 
                return {"code":200,"message":"Items Fetched Successfully","res":{"data":resp['Items']}}
            else:
                return {"code":400,"message":"Empty Data. No data found"}
        print(resp) 
    except Exception as e: 
        return {"code":400,"message":f"Exception Occurs {repr(e)}"}
    
    

@copydetect_router.post("/getinterndetails")
def getInternDetails(internID:str=Form()): 
    print("Intern ID is ",internID)
    resp = aws_controller.getItemFromDynamoDB('Plagiarism_Detector',{"Intern_ID":internID})
    print(resp) 
    return resp 