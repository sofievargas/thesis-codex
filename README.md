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


To see the data visualization, navigate to the folder that index.html is located and double click. Alternatively, through VS Code right click index.html and select 'Open with Live Server' .

**Example Postman Requests**

<img width="747" height="599" alt="Screenshot 2026-03-24 at 11 09 35 AM" src="https://github.com/user-attachments/assets/e9d6032e-40c8-4d45-9f2e-e53530188d92" />

<img width="836" height="526" alt="Screenshot 2026-03-24 at 11 13 18 AM" src="https://github.com/user-attachments/assets/a93ad0a5-4853-4138-ae19-655a1ad5c6f8" />

<img width="850" height="592" alt="Screenshot 2026-03-24 at 11 15 14 AM" src="https://github.com/user-attachments/assets/cd098ce7-dd79-4cf9-8ed2-a7066fbaf272" />



