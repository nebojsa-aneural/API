# Aneurala REST API

Serving segmentation models

## Run the server in the development
To start the server run
> python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

### Setup
Project requires ".env" file in the root in order to work.
You can 'touch .env' or create file otherwise and have the following content inside:

<- BEGINING OF FILE->
DATABASE=aneural
USERNAME=aneural
PASSWORD=aneural
HOSTNAME=localhost
<- END OF FILE ->

where all values should be set appropriately for your environment