from fastapi import FastAPI,Form,UploadFile,File,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional  
from fastapi import APIRouter, Request, status, Form, HTTPException
from Router.Plagiarism import copydetect_router
from Router.FileProcessor import filer_router 
from Controllers.AWS import aws_controller 
from Controllers.Plagiarism import plagiarism_controller 
from Controllers.FileProcessor import htmlparser_controller
from Controllers.FileProcessor import csvfileparser_controller

app = FastAPI() 

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filer_router.file_router)
app.include_router(copydetect_router.copydetect_router)

@app.post("/testing") 
async def testing(req:Request): 
    # data = await req.json() 
    # aws_controller.downloadFoldersfroms3("plagiarism-detector","INTERN_PORTAL_FY23")
    resp = plagiarism_controller.detectPlagiarism()
    return resp 
    # out=htmlparser_controller.parseHTML("DiwaG_900555NageshA_900366.html")
    # print(out)
    # resp=aws_controller.insertIntoDynamoDB("Plagiarism_Detector",{"Intern_ID":"900375","Report":[{"percentage":[{"900375":"98"}]}]})
    # resp = aws_controller.updateItemInDynamoDB("Plagiarism_Detector",{"Intern_ID":"900999"},{"Report":[{"percentage":[{"900375":"90"}]}]})
    # print(resp)
    # print(data)  
    # return {"res":"hello I am from testing!!!...","code":200}