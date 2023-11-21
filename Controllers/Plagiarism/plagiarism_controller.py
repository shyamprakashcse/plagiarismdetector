import os 
import shutil 
from copydetect import CopyDetector  
from Controllers.FileProcessor import htmlparser_controller
from Controllers.AWS import aws_controller 

def get_initial_level_folders(directory):
    folders = []
    for root, dirs, files in os.walk(directory):
        levels = root.split(os.sep)
        if len(levels) - len(directory.split(os.sep)) == 0:
            folders.extend([os.path.join(root, dir) for dir in dirs])

    return folders

def detectPlagiarism():
    test_directory = r"D:/Plagiarism_Detector/INTERN_PORTAL_FY23" 
    reference_directory = r"D:/Plagiarism_Detector/INTERN_PORTAL_FY23" 
    source_folder_list = get_initial_level_folders(test_directory)
    destination_folder_list = get_initial_level_folders(reference_directory)
    print(source_folder_list)  
    
    try: 
        
        for test in source_folder_list: 
            score_report = {}
            overAllScore = 0
            count = 0 
            for ref in destination_folder_list: 
                if test!=ref:
                    detector = CopyDetector(test_dirs=[test],ref_dirs=[ref],display_t=0.0, autoopen=False)
                    detector.run() 
                    detector.generate_html_report() 
                    source_candidate = os.path.basename(test) 
                    destination_candidate = os.path.basename(ref)
                    print(source_candidate,destination_candidate)
                    generated_Report_Name = source_candidate+destination_candidate+".html"
                    os.rename("report.html", generated_Report_Name)  
                    oneToOneScore = htmlparser_controller.parseHTML(generated_Report_Name) 
                    if oneToOneScore["code"]==200: 
                        avg_scores = oneToOneScore["res"]  
                        print(avg_scores) 
                        score_report[destination_candidate] = avg_scores["A_Avg"]
                        overAllScore+=float(avg_scores["A_Avg"])
                        count+=1
                        # aws_controller.updateItemInDynamoDB("Plagiarism_Detector",{"Intern_ID":source_candidate},{"Report":{"Percentage"}})
                        
                    else: 
                        print(f"error occurs while parsing an html file {generated_Report_Name}") 
                        print(oneToOneScore) 
            score_report[source_candidate] = "100" 
            OverAllAvg = str(overAllScore/count)
            resp = aws_controller.updateItemInDynamoDB("Plagiarism_Detector",{"Intern_ID":source_candidate},{"Report":score_report,"Report_Status":"True","OverAllAvg":OverAllAvg})
            print(resp)
            print(score_report) 
            print("**************************************************")
            print("******************************************")
        
        return {"code":200,"message":"Computed Report Successfully..."}   
                    
    except Exception as e:

        print("Error: Command failed with non-zero exit code.")

        print("Error message:", repr(e))
    
   
