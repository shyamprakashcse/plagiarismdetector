from bs4 import BeautifulSoup

# Open the HTML file

def parseHTML(filepath): 
    try:
        with open(filepath, 'r') as file:
            html_content = file.read() 
            soup = BeautifulSoup(html_content, 'html.parser') 
            percentage_elements = soup.find_all('b')
            percentages = [percentage.text for percentage in percentage_elements] 
            percentages = [float(i.strip('%')) for i in percentages]
            A_Files_Scores = []
            B_Files_Scores = [] 
            for i in range(len(percentages)):
                if i%2==0: 
                    A_Files_Scores.append(percentages[i]) 
                else: 
                    B_Files_Scores.append(percentages[i]) 
                    
            A_Avg = str(sum(A_Files_Scores)//len(A_Files_Scores))
            B_Avg = str(sum(B_Files_Scores)//len(B_Files_Scores))
            return {"code":200,"message":"Parsed Successfully","res":{"A_Avg":A_Avg,"B_Avg":B_Avg}}
    except Exception as e: 
        print(repr(e))
        return {"code":400,"message":"Exception Occurs "+repr(e)}