# Aneural REST API

Serving segmentation models

## Run the server in the development
To start the server run
> python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

### Setup
Project requires ".env" file in the root in order to work.
You can 'touch .env' or create file otherwise and have the following content inside:

<- BEGINING OF FILE-><br/>
DATABASE=aneural<br/>
USERNAME=aneural<br/>
PASSWORD=aneural<br/>
HOSTNAME=localhost<br/>
<- END OF FILE -><br/>

where all values should be set appropriately for your environment

### Database setup

Install PostgreSQL on your system.
If you are on Mac or Linux use brew or apt to install it.
Once installed, execute following commands:

Create database:
> CREATE DATABASE aneural   WITH ENCODING=‘UTF8’;
Add role (crate user):
> CREATE USER aneural WITH PASSWORD ‘aneural’
Grant privileges to new user on the database:
> GRANT ALL PRIVILEGES ON DATABASE aneural TO aneural;