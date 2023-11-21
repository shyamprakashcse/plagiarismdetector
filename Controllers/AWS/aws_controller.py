import boto3 
from boto3.dynamodb.conditions import Key
from io import StringIO 
from io import BytesIO 
from cloudpathlib import CloudPath
from config import config 
import pandas as pd 
import os 

dynamo_client  =  boto3.resource(
service_name = 'dynamodb',
region_name = 'ap-south-1',
aws_access_key_id = config["DIGIVERZ_AWSACCESSKEY"],
aws_secret_access_key = config["DIGIVERZ_AWSSECRETKEY"]) 

s3_client  =  boto3.client(
service_name = 's3',
aws_access_key_id = config["DIGIVERZ_AWSACCESSKEY"],
aws_secret_access_key = config["DIGIVERZ_AWSSECRETKEY"]) 


def insertIntoDynamoDB(table_name,item):
    try:
        dynamodb_table = dynamo_client.Table(table_name) 
        res = dynamodb_table.put_item(Item=item)
        print("res from dynamo db")
        print(res)
        if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"code":200,"message":"inserted item successfully"}
        else: 
            return {"code":400,"message":"Failed to Insert an Item"} 
    except Exception as e: 
        return {"code":400,"message":repr(e)} 
    
def insertMultipleIntoDynamoDB(table_name,itemlist): 
    try: 
        dynamodb_table = dynamo_client.Table(table_name) 
        with dynamodb_table.batch_writer() as batch:
            for item in itemlist:
                batch.put_item(Item=item)
    except Exception as e: 
        return {"code":400,"message":repr(e)}

def getItemFromDynamoDB(table_name,item): 
    try: 
        
        dynamodb_table = dynamo_client.Table(table_name)
        res = dynamodb_table.get_item(Key=item)
        if 'Item' in res: 
            return {"code":200,"message":"Item Found","res":res['Item']} 
        else: 
            return {"code":400,"message":"No Item Found!"} 

    except Exception as e: 
        return {"code":400,"message":repr(e)}   

def scanItemFromDynamoDB(table_name): 
    try: 
        resp = dynamo_client.scan({'TableName':table_name}) 
        print(resp) 
        return "helok"
    except Exception as e: 
        print(f"Exception Occurs {repr(e)}") 
        return {"code":400,"message":f"Exception Occurs due to {repr(e)}"}

def GSIQueryingOnDynamoDB(table_name,index_name,colname,value,condition): 
    try: 
        dynamodb_table = dynamo_client.Table(table_name)
        
        if condition == "==":
            res = dynamodb_table.query( IndexName=index_name,
                    KeyConditionExpression=Key(colname).eq(value)) 
        elif condition == "<":
            res = dynamodb_table.query( IndexName=index_name,
                    KeyConditionExpression=Key(colname).lt(value))
        elif condition == ">": 
            res = dynamodb_table.query( IndexName=index_name,
                    KeyConditionExpression=Key(colname).gt(value))
        elif condition == "<=":
            res = dynamodb_table.query( IndexName=index_name,
                    KeyConditionExpression=Key(colname).lte(value))
        elif condition == ">=":
            res = dynamodb_table.query( IndexName=index_name,
                    KeyConditionExpression=Key(colname).gte(value))

        return res 
    

    except Exception as e:
        return e 



def uploadCSVToS3(bucketName,df,path):
    csv_buf = StringIO()
    df.to_csv(csv_buf,header=True,index=False)
    csv_buf.seek(0)
    res = s3_client.put_object(Bucket=bucketName,Body=csv_buf.getvalue(),Key=path)  
    print(res)
    if res["ResponseMetadata"]["HTTPStatusCode"] == 200: 
        return {"code":200,"message":"file uploaded to s3 bucket successfully"}
    else:
        return {"code":400,"message":"Failed to upload a file to s3 bucket"}

def pourCSVFromS3(bucketName,path):
    try:
        f = BytesIO()
        s3_client.download_fileobj(bucketName,path,f) 
        bytes_data = f.getvalue()
        s=str(bytes_data,'utf-8')
        data = StringIO(s) 
        df=pd.read_csv(data) 
        return {"code":200,"message":"Fetched Successfully","df":df} 
    except Exception as e:
        res = repr(e)
        return {"code":400,"message":res}

def uploadImageToS3(bucket_name,image_file,file_name):
    try:
        resp=s3_client.put_object(Bucket=bucket_name,Body=image_file,Key=file_name)
        if resp["ResponseMetadata"]["HTTPStatusCode"]==200:
            return {"code":200,"message":"Successfully Uploaded a file"}
        else:
            return {"code":400,"message":"Error Occurs while Uploading"}
    except Exception as e:
        print(repr(e))
        print("Exception arises while uploading to S3")
        return {"code":400,"message":"Exception arises while uploading to S3 "+repr(e)} 

def pourImageFromS3():
    pass




def get_update_params(body):
    """Given a dictionary we generate an update expression and a dict of values
    to update a dynamodb table.

    Params:
        body (dict): Parameters to use for formatting.

    Returns:
        update expression, dict of values.
    """
    update_expression = ["set "]
    update_values = dict()

    for key, val in body.items():
        update_expression.append(f" #{key} = :{key},")
        update_values[f":{key}"] = val

    return "".join(update_expression)[:-1], update_values

def updateItemInDynamoDB(tablename,keyitem,updateditem): 

    dynamodb_table = dynamo_client.Table(tablename)
    # item = {"aspect":{"hello":"updated"},"status":"COMPLETED"} 
    expattribute = {}
    for key in updateditem: 
        expattribute["#"+key]=key 

    a, v = get_update_params(updateditem) 
    response = dynamodb_table.update_item(
        # Key = { "runid":"13022023203321","filename":"Womens Clothing E-Commerce Reviews"}, 
        Key = keyitem, 
        UpdateExpression=a,
        ExpressionAttributeValues=dict(v), 
        ExpressionAttributeNames = expattribute 
    )
    print(a)
    print(v) 
    print(response)   
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200: 
        return {"code":200,"message":"updated item successfully"} 
    else: 
        return {"code":400,"message":"update failed"}
    
    

def downloadFoldersfroms3(bucketName,folderName):  
    s3FolderPath = f"s3://{bucketName}/{folderName}/" 
    localdirectory = f"./{folderName}"
    if not os.path.exists(folderName): 
        os.makedirs(folderName) 
        print("Folder has been created successfully...") 
        
    cp = CloudPath(s3FolderPath)
    
    resp = cp.download_to(localdirectory)
    print(resp) 
    return resp; 
    
    
def upload_file_to_s3(local_file_path, s3_bucket, s3_key):
    s3_client.upload_file(local_file_path, s3_bucket, s3_key)

# Function to recursively upload a local folder and its contents to S3
def upload_folder_to_s3(local_folder, s3_bucket, s3_prefix):
    # Get a list of all items (files and directories) in the folder
    # s3_client.put_object(Bucket='plagiarism-detector',Key='INTERN_PORTAL_FY23/src/folder1/folder2/')
    
    try:
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                # Get the full path of each file
                file_path = os.path.join(root, file)
                file_path = file_path.replace("\\","/") 
                folders = file_path.split("/")  
                folder_path = '/'.join(folders[:-1])+'/'
                # print(folder_path)
                s3_client.put_object(Bucket=s3_bucket,Key=folder_path)
                s3_client.upload_file(file_path,s3_bucket,file_path) 
                
        return {"code":200,"message":"Uploaded Successfully"}
            
    except Exception as e: 
        return {"code":400,"message": f"Exception Occurs {repr(e)}"}
    



def deleteFoldersInS3(bucketName,deleteFolderS3Path): 
    try:
        objects_to_delete = []

        response = s3_client.list_objects_v2(Bucket=bucketName, Prefix=deleteFolderS3Path)
        for obj in response.get('Contents', []):
            objects_to_delete.append({'Key': obj['Key']})

        # Delete the objects in the folder
        if objects_to_delete:
            s3_client.delete_objects(Bucket=bucketName, Delete={'Objects': objects_to_delete}) 
            s3_client.delete_object(Bucket=bucketName, Key=deleteFolderS3Path)  
            
        return {"code":200,"message":"Deleted Objects Successfully"}
    except Exception as e: 
        return {"code":400,"message":"Exception Occurs while Deleting a folder from S3."}

