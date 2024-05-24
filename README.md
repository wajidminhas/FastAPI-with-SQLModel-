


# TODO API

This project is a simple API built with FastAPI and PostgreSQL using Docker. The API allows for basic CRUD operations on a to-do list.

## Project Structure

- `api`: The FastAPI service handling the application logic.
- `postgres_db`: The PostgreSQL database service storing the to-do items.

## Prerequisites

- Docker and Docker Compose installed on your machine.

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/yourusername/myapi.git
cd myapi


docker-compose up --build

 ////////////////////////////
 
 This command will:

	1.	Build the Docker image for the FastAPI service.
	2.	Start the FastAPI service on port 8000.
	3.	Start the PostgreSQL database on port 5433.
	
#API Endpoints

	Once the containers are running, the FastAPI application will 				be accessible at http://localhost:8000.

#Available Endpoints

	1.	GET /todos: Retrieve all to-do items.
	2.	GET /todos/{id}: Retrieve a single to-do item by ID.
	3.	POST /todos: Create a new to-do item.
	4.	PUT /todos/{id}: Update an existing to-do item by ID.
	5.	DELETE /todos/{id}: Delete a to-do item by ID.

#Environment Variables

	The PostgreSQL container is configured with the following 	environment variables:

	POSTGRES_USER=wajidminhas
	POSTGRES_PASSWORD=my_password
	POSTGRES_DB=tododatabase
	You can change these values in the docker-compose.yml file if needed.

#Volumes

	The PostgreSQL data is stored in a Docker volume to persist data across container restarts. The volume is defined in the docker-compose.yml file:


	volumes:
  	  postgres_db:
	    driver: local
	    
#Networks
	Both the API and PostgreSQL services are connected to a Docker network for internal communication:
	networks:
  	  my-api-net:
    	    driver: bridge
    	    
#Stopping the Containers
	To stop the running containers, use the following command:
	
	docker-compose down

#Troubleshooting

	1.	Ensure Docker and Docker Compose are correctly installed and running on your machine.
	2.	Check if the ports 8000 and 5433 are free. If not, modify the docker-compose.yml to use 			different ports.
	3.	Review the container logs for any errors using the command:

	docker-compose logs
	
	#Contributing
	
	Feel free to open issues or submit pull requests if you find any bugs or have improvements.
	
	 `https://github.com/wajidminhas/myapi.git` 
	 `shanitent667@example.com` 

	



	



