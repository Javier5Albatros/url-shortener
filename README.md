# Url Shortener 
Url shortener made with **FastAPI** for CoreDumped Academy 2020

Quickstart
----------

First clone the project and install de dependencies
You should have a mongodb server

    git clone https://github.com/Javier5Albatros/url-shortener.git
    cd url-shortener
    pip install -r requirements.txt


To run the web application in debug use:

    uvicorn app.main:app --reload

or:
	
    cd app
    uvicorn main:app --reload
Run tests
---------
You can go to http://localhost:8000/docs


Project Structure
---------
    app
    ├── api              - web related stuff.
    │   └── routes       - web routes.
    ├── db               - db related stuff.
    ├── models           - pydantic models for this application
    ├── services         - logic that is not just crud related.
    └── main.py          - FastAPI application creation and configuration.