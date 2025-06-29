from fastapi import FastAPI, Request, Path, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Patient(BaseModel):
    
    id : Annotated[str, Field(...,description='patient id',examples=['P1'])]
    name : Annotated[str, Field(...,description='patiend name',exmpales=['sam'])]
    city : Annotated[str, Field(...,description='patient living city',examples=['ahmedabad'])]
    age : Annotated[int, Field(...,description='patient age',examples=['23'],gt=0,lt=100)]
    gender : Annotated[Literal['male','female','other'],Field(...,description='gender of the patient',examples=['male'])]
    height : Annotated[float, Field(...,description='patiend height in meters',examples=['1.67'])]
    weight : Annotated[float, Field(...,description='patient weight in kilogram',examples=['70.0'])]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
        
    @computed_field
    @property
    def verdict(self) -> str:
        if self.weight < 18.5:
            return 'underweight'
        elif self.weight < 30:
            return 'normal'
        else:
            return 'obese'
        
class PatientUpdate(BaseModel):
    name : Annotated[Optional[str], Field(description='patient name', examples=['sam'])]
    city : Annotated[Optional[str], Field(description='patient living city', examples=['ahmedabad'])]
    age : Annotated[Optional[int], Field(description='patient age', examples=['23'],gt=0,lt=100)]
    gender : Annotated[Optional[Literal['male','female','other']], Field(description='patient gender',default='other')]
    height : Annotated[Optional[float], Field(description='patient height in meters',examples=['1.67'])]
    weight : Annotated[Optional[float], Field(description='patient weight in kilogram',examples=['70.0'])]
    
def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
        return data
    
def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.get('/',response_class=HTMLResponse)
async def home(request : Request):
    return templates.TemplateResponse('index.html',{'request':request,'message':'hello world'})

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def patient_id_view(patient_id: str = Path(...,description="patient id",example='P001')):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="patient not found")

@app.get('/sort')
def sort_patient(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'),order: str = Query('asc', description='sort in asc or desc order')):
    
    valid_fields = ['height','weight','bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='invalid order selected')
    
    data = load_data()
    
    sort_order = True if order == 'desc' else False
    
    sort_data = sorted(data.values(), key=lambda x:x.get(sort_by, 0),reverse=sort_order)
    
    return sort_data

@app.delete('delete/{patient_id}')
def delete_patient(patient_id : str):
    
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient not found')
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={'message':'patient deleted'})