FROM python:3.10 


WORKDIR /Plagiarism_Detector
COPY ./requirements.txt /Plagiarism_Detector
RUN pip install -r requirements.txt 
COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]