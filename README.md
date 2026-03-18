**Overview**

This project is a FastAPI-based backend service that collects user-submitted translation entries and stores them in a Neo4j graph database.
Each entry includes:
City (derived from client IP address)
Original language
Target language
Translation word

The system also provides analytics endpoints to generate reports such as:
Most common cities (location frequency)
Most common translated words

These analytics can be consumed by frontend tools to generate visualizations such as pie charts and bar graphs.

**Setup**
1. Clone the repository

  git clone https://github.com/sofievargas/thesis-codex.git
  
  cd thesis-codex

  
2. Create and activate a virtual environment


   python -m venv venv

   source venv/bin/activate   # Mac/Linux

   venv\Scripts\activate      # Windows
   
4. Install dependencies:
   
  pip install -r requirements.txt
  
4. Configure environment variables
 
  Create a .env file in the root directory:

  NEO4J_URI=your_neo4j_uri
  
  NEO4J_USER=your_username
 
  NEO4J_PASSWORD=your_password


**Start the FastAPI server:**

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Interactive API docs:

http://127.0.0.1:8000/docs

**Running with ngrok (for Accurate Location Detection)**

Download from:
https://ngrok.com/download

Start API

uvicorn app.main:app --reload

Start ngrok

ngrok http 8000

This will create a URL (i.e. https://homey-nonconvective-rueben.ngrok-free.dev ) . Then append /docs to access the Interactive API SwaggerUI 




