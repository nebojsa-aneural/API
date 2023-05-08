import os
import uuid
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
import base64
from pydantic import BaseModel
from typing import Optional

import aiofiles
from dotenv import load_dotenv
import asyncpg

load_dotenv()

database = os.environ['DATABASE']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
hostname = os.environ['HOSTNAME']

async def connect_to_db():
    return await asyncpg.connect(f"postgres://{username}:{password}@{hostname}/{database}")

app = FastAPI()

origins = [
    "http://localhost:8080",  # Update the port to match the one you are using
    "https://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check and create storage directory
storageDir = "../storage"
if not os.path.exists(storageDir):
    os.makedirs(storageDir)

class ApiResponse(BaseModel):
    message: str
    error: Optional[str] = None
    payload: Optional[dict] = None

@app.post("/upload", response_model=ApiResponse)
async def uploadImage(image: UploadFile = File(...)):

    try:
        # Save the uploaded image
        inputImageName = f"{uuid.uuid4()}{os.path.splitext(image.filename)[-1]}"
        inputImagePath = os.path.join(storageDir, inputImageName)
        outputImageName = f"{os.path.splitext(inputImageName)[0]}_rendered{os.path.splitext(inputImageName)[-1]}"
        outputImagePath = os.path.join(storageDir, outputImageName)

        async with aiofiles.open(inputImagePath, "wb") as f:
            content = await image.read()
            await f.write(content)

        # Create a new record in the tasks table
        jobUuid = uuid.uuid4()
        requestDateTime = datetime.now()
        deadlineDateTime = requestDateTime + timedelta(hours=24)

        connection = await connect_to_db()
        await connection.execute('''
            INSERT INTO tasks ("Uuid", "Client", "ModelPath", "RequestDateTime", "DeadlineDateTime", "InputImagePath", "OutputImagePath", "Status", "Priority")
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
        ''', jobUuid, 'WebClient', 'model/model_pretrained_True_epochs_103.pth', requestDateTime, deadlineDateTime, inputImagePath, outputImagePath, 'pending', 100)

        await connection.close()

        return ApiResponse(message="success", payload={"uuid": str(jobUuid)})

    except Exception as e:
        return ApiResponse(message="failure", error=str(e), payload={"uuid": None})

@app.get("/download/{jobUuid}", response_model=ApiResponse)
async def downloadImage(jobUuid: str):
    try:
        connection = await connect_to_db()
        task = await connection.fetchrow("""
            SELECT * FROM tasks
            WHERE "Uuid" = $1;
        """, jobUuid)

        if not task:
            raise HTTPException(status_code=404, detail="Image not found")

        status = task["Status"]

        if status == "success":
            async with aiofiles.open(task["OutputImagePath"], "rb") as f:
                renderedImageData = await f.read()

            # build source jpg path from rendered
            sourceImagePath = task["OutputImagePath"].replace("_rendered", "_source")
            async with aiofiles.open(sourceImagePath, "rb") as f:
                sourceImageData = await f.read()
            
            b64Image = base64.b64encode(renderedImageData).decode("utf-8")
            b64Source = base64.b64encode(sourceImageData).decode("utf-8")
            return ApiResponse(message=status, payload={"uuid": jobUuid, "images": {'rendered': b64Image, 'source': b64Source}})

        await connection.close()

        return ApiResponse(message=status, payload={"uuid": jobUuid})

    except Exception as e:
        return ApiResponse(message="failure", error=str(e), payload={"uuid": jobUuid})
