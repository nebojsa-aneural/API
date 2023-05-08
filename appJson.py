from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

class UploadRequest(BaseModel):
    imageBase64: str
    fileName: str

# Alternative to multipart/form-data upload form of binary data: JSON base64 encoded files
@app.post("/upload", response_model=ApiResponse)
async def uploadImage(request: UploadRequest):
    try:
        # Check and create storage directory
        storageDir = "storage"
        if not os.path.exists(storageDir):
            os.makedirs(storageDir)

        # Decode the base64 image
        imageData = base64.b64decode(request.imageBase64)

        # Save the uploaded image
        inputImageName = f"{uuid.uuid4()}{os.path.splitext(request.fileName)[-1]}"
        inputImagePath = os.path.join(storageDir, inputImageName)
        outputImageName = f"{os.path.splitext(inputImageName)[0]}_rendered{os.path.splitext(inputImageName)[-1]}"
        outputImagePath = os.path.join(storageDir, outputImageName)

        async with aiofiles.open(inputImagePath, "wb") as f:
            await f.write(imageData)

        # Create a new record in the tasks table
        jobUuid = uuid.uuid4()
        requestDateTime = datetime.now()
        deadlineDateTime = requestDateTime + timedelta(hours=24)

        connection = await connectToDb()
        await connection.execute("""
            INSERT INTO tasks (Uuid, Client, ModelPath, RequestDateTime, DeadlineDateTime, InputImagePath, OutputImagePath, Status, Priority)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);
        """, jobUuid, 'WebClient', 'model/model.h5', requestDateTime, deadlineDateTime, inputImagePath, outputImagePath, 'pending', 'normal')

        await connection.close()

        return ApiResponse(message="success", payload={"uuid": str(jobUuid)})

    except Exception as e:
        return ApiResponse(message="failure", error=str(e), payload={"uuid": None})
