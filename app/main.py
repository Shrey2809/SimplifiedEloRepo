from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import Pickems
from pydantic import BaseModel
from sqlalchemy import func
import uuid

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define Pydantic model for Pickems
class PickemCreate(BaseModel):
    Team3_0: str
    Team0_3: str
    Top8Teams: list[str]
    Quarters: list[str] = None
    Semis: list[str] = None
    Final: str = None
    Points: int = 0


# Define Pydantic model for PickemResponse
class PickemResponse(BaseModel):
    UserName: str
    UserKey: str
    Team3_0: str
    Team0_3: str
    Top8Teams: list[str]
    Quarters: list[str] = None
    Semis: list[str] = None
    Final: str = None
    Points: int

# Define a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI!"}


# Add new user pickems
@app.post("/pickems/{user_name}", status_code=status.HTTP_201_CREATED)
def create_pickems(user_name: str, pickem: PickemCreate, db: Session = Depends(get_db)):
    # Generate a unique user key -  6 digits numbers only
    user_key = str(uuid.uuid4().int)[:6]
    print(user_name, user_key)
    
    # Check if a pickem already exists for the user
    existing_pickem = db.query(Pickems).filter(
        func.lower(Pickems.UserName) == user_name.lower()
    ).first()
    
    if existing_pickem:
        raise HTTPException(status_code=400, detail="Pickem already exists for this user.")
    
    # Create a new pickem record
    new_pickem = Pickems(
        UserName=user_name,
        UserKey=user_key,
        Team3_0=pickem.Team3_0,
        Team0_3=pickem.Team0_3,
        Team2=pickem.Top8Teams[0] if len(pickem.Top8Teams) > 0 else None,
        Team3=pickem.Top8Teams[1] if len(pickem.Top8Teams) > 1 else None,
        Team4=pickem.Top8Teams[2] if len(pickem.Top8Teams) > 2 else None,
        Team5=pickem.Top8Teams[3] if len(pickem.Top8Teams) > 3 else None,
        Team6=pickem.Top8Teams[4] if len(pickem.Top8Teams) > 4 else None,
        Team7=pickem.Top8Teams[5] if len(pickem.Top8Teams) > 5 else None,
        Team8=pickem.Top8Teams[6] if len(pickem.Top8Teams) > 6 else None,
        QF1=pickem.Quarters[0] if pickem.Quarters is not None else None,
        QF2=pickem.Quarters[1] if pickem.Quarters is not None else None,
        QF3=pickem.Quarters[2] if pickem.Quarters is not None else None,
        QF4=pickem.Quarters[3] if pickem.Quarters is not None else None,
        SF1=pickem.Semis[0] if pickem.Semis is not None else None,
        SF2=pickem.Semis[1] if pickem.Semis is not None else None,
        Final=pickem.Final if pickem.Final is not None else None,
        Points=0
    )
    print("data added")
    
    db.add(new_pickem)
    db.commit()
    db.refresh(new_pickem)
    
    return {
        "UserName": new_pickem.UserName,
        "UserKey": user_key,  # Return the generated user key
        "Team3_0": new_pickem.Team3_0,
        "Team0_3": new_pickem.Team0_3,
        "Top8Teams": [new_pickem.Team2, new_pickem.Team3, new_pickem.Team4, new_pickem.Team5, new_pickem.Team6, new_pickem.Team7, new_pickem.Team8],
        "Quarters": [new_pickem.QF1, new_pickem.QF2, new_pickem.QF3, new_pickem.QF4],
        "Semis": [new_pickem.SF1, new_pickem.SF2],
        "Final": new_pickem.Final,
        "Points": 0
    }

@app.put("/pickems/{user_name}-{user_key}", status_code=status.HTTP_200_OK)
def update_pickems(user_name: str, user_key: int, pickem: PickemCreate, db: Session = Depends(get_db)):
    # Fetch the existing pickem record
    existing_pickem = db.query(Pickems).filter(
        func.lower(Pickems.UserName) == user_name.lower(),
        Pickems.UserKey == user_key  # Ensure user_key is treated as an integer
    ).first()

    # Check if the pickem exists
    if existing_pickem is None:
        raise HTTPException(status_code=404, detail="Pickem not found")

    # Update the existing pickem record
    existing_pickem.Team3_0 = pickem.Team3_0
    existing_pickem.Team0_3 = pickem.Team0_3
    existing_pickem.Team2 = pickem.Top8Teams[0] if len(pickem.Top8Teams) > 0 else None
    existing_pickem.Team3 = pickem.Top8Teams[1] if len(pickem.Top8Teams) > 1 else None
    existing_pickem.Team4 = pickem.Top8Teams[2] if len(pickem.Top8Teams) > 2 else None
    existing_pickem.Team5 = pickem.Top8Teams[3] if len(pickem.Top8Teams) > 3 else None
    existing_pickem.Team6 = pickem.Top8Teams[4] if len(pickem.Top8Teams) > 4 else None
    existing_pickem.Team7 = pickem.Top8Teams[5] if len(pickem.Top8Teams) > 5 else None
    existing_pickem.Team8 = pickem.Top8Teams[6] if len(pickem.Top8Teams) > 6 else None
    if pickem.Quarters is not None:
        existing_pickem.QF1 = pickem.Quarters[0] if len(pickem.Quarters) > 0 else None
        existing_pickem.QF2 = pickem.Quarters[1] if len(pickem.Quarters) > 1 else None
        existing_pickem.QF3 = pickem.Quarters[2] if len(pickem.Quarters) > 2 else None
        existing_pickem.QF4 = pickem.Quarters[3] if len(pickem.Quarters) > 3 else None
        existing_pickem.SF1 = pickem.Semis[0] if len(pickem.Semis) > 0 else None
        existing_pickem.SF2 = pickem.Semis[1] if len(pickem.Semis) > 1 else None
        existing_pickem.Final = pickem.Final if pickem.Final is not None else None  # Update the final if provided

    existing_pickem.Points = pickem.Points  # Update points if necessary

    # Commit the changes to the database
    db.commit()
    db.refresh(existing_pickem)

    # Return the updated pickem, converting UserKey to string
    return {
        "UserName": existing_pickem.UserName,
        "UserKey": str(existing_pickem.UserKey),  # Convert to string for the response
        "Team3_0": existing_pickem.Team3_0,
        "Team0_3": existing_pickem.Team0_3,
        "Top8Teams": [
            existing_pickem.Team2,
            existing_pickem.Team3,
            existing_pickem.Team4,
            existing_pickem.Team5,
            existing_pickem.Team6,
            existing_pickem.Team7,
            existing_pickem.Team8,
        ],
        "Quarters": [
            existing_pickem.QF1,
            existing_pickem.QF2,
            existing_pickem.QF3,
            existing_pickem.QF4,
        ],
        "Semis": [existing_pickem.SF1, existing_pickem.SF2],
        "Final": existing_pickem.Final,
        "Points": existing_pickem.Points,
    }

@app.put("/pickems/admin/{user_name}-{user_key}", status_code=status.HTTP_200_OK)
def update_pickems(user_name: str, user_key: int, pickem: PickemCreate, db: Session = Depends(get_db)):
    # Fetch the existing pickem record
    existing_pickem = db.query(Pickems).filter(
        func.lower(Pickems.UserName) == user_name.lower(),
        Pickems.UserKey == user_key  # Ensure user_key is treated as an integer
    ).first()
    
    # Check if the pickem exists
    if existing_pickem is None:
        # Create a new pickem record
        new_pickem = Pickems(
            UserName=user_name,
            UserKey=user_key,
            Team3_0=pickem.Team3_0,
            Team0_3=pickem.Team0_3,
            Team2=pickem.Top8Teams[0] if len(pickem.Top8Teams) > 0 else None,
            Team3=pickem.Top8Teams[1] if len(pickem.Top8Teams) > 1 else None,
            Team4=pickem.Top8Teams[2] if len(pickem.Top8Teams) > 2 else None,
            Team5=pickem.Top8Teams[3] if len(pickem.Top8Teams) > 3 else None,
            Team6=pickem.Top8Teams[4] if len(pickem.Top8Teams) > 4 else None,
            Team7=pickem.Top8Teams[5] if len(pickem.Top8Teams) > 5 else None,
            Team8=pickem.Top8Teams[6] if len(pickem.Top8Teams) > 6 else None,
            QF1=pickem.Quarters[0] if pickem.Quarters is not None else None,
            QF2=pickem.Quarters[1] if pickem.Quarters is not None else None,
            QF3=pickem.Quarters[2] if pickem.Quarters is not None else None,
            QF4=pickem.Quarters[3] if pickem.Quarters is not None else None,
            SF1=pickem.Semis[0] if pickem.Semis is not None else None,
            SF2=pickem.Semis[1] if pickem.Semis is not None else None,
            Final=pickem.Final if pickem.Final is not None else None,
            Points=0
        )
        print("data added")
        
        db.add(new_pickem)
        db.commit()
        db.refresh(new_pickem)
        
        return {
            "UserName": new_pickem.UserName,
            "UserKey": user_key,  # Return the generated user key
            "Team3_0": new_pickem.Team3_0,
            "Team0_3": new_pickem.Team0_3,
            "Top8Teams": [new_pickem.Team2, new_pickem.Team3, new_pickem.Team4, new_pickem.Team5, new_pickem.Team6, new_pickem.Team7, new_pickem.Team8],
            "Quarters": [new_pickem.QF1, new_pickem.QF2, new_pickem.QF3, new_pickem.QF4],
            "Semis": [new_pickem.SF1, new_pickem.SF2],
            "Final": new_pickem.Final,
            "Points": 0
        }

# Get all pickems for a user
@app.get("/pickems/{user_name}-{user_key}")
def read_pickems(user_name: str, user_key: str, db: Session = Depends(get_db)):
    pickems = db.query(Pickems).filter(
        func.lower(Pickems.UserName) == user_name.lower(),
        Pickems.UserKey == user_key
    ).first()

    returnObject = {
        "UserName": pickems.UserName,
        "UserKey": pickems.UserKey,
        "Team3_0": pickems.Team3_0,
        "Team0_3": pickems.Team0_3,
        "Top8Teams": [pickems.Team2, pickems.Team3, pickems.Team4, pickems.Team5, pickems.Team6, pickems.Team7, pickems.Team8],
        "Quarters": [pickems.QF1, pickems.QF2, pickems.QF3, pickems.QF4],
        "Semis": [pickems.SF1, pickems.SF2],
        "Final": pickems.Final,
        "Points": pickems.Points
    }
    
    if pickems is None:
        raise HTTPException(status_code=404, detail="Pickems not found")
    return returnObject

# Get all pickems
@app.get("/pickems")
def read_pickems(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    pickems = db.query(Pickems).offset(skip).limit(limit).all()
    return pickems

# Update the points for a user
@app.put("/pickems/{user_name}-{user_key}/points/{points}")
def update_points(user_name: str, user_key: str, points: int, db: Session = Depends(get_db)):
    pickems = db.query(Pickems).filter(
        func.lower(Pickems.UserName) == user_name.lower(),
        Pickems.UserKey == user_key
    ).first()

    if pickems is None:
        raise HTTPException(status_code=404, detail="Pickems not found")

    pickems.Points = points
    db.commit()
    db.refresh(pickems)

    return pickems.Points

# Get count of all pickems
@app.get("/pickems/count")
def read_pickems_count(db: Session = Depends(get_db)):
    return {"count": db.query(Pickems).count()}

