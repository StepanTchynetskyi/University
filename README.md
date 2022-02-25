# University

## Database Schema
![alt text](https://github.com/StepanTchynetskyi/University/blob/main/db_schema_img/database_schema.png?raw=true)


### To start project locally with docker-compose add .env.docker file with such content
```
SECRET_KEY=YOUR_SECRET_KEY(uuid4)
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY(uuid4)
DATABASE_URI=postgresql://{username}:{password}@db:{port}/{db_name}
APP_SETTINGS=application.config.DevelopmentConfig
POSTGRES_USER=YOUR_POSTGRES_USER
POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD
POSTGRES_DB=YOUR_DB_NAME
```

### To start project with ``flask run`` add .env.local file with such content:
```
SECRET_KEY=YOUR_SECRET_KEY(uuid4)
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY(uuid4)
DATABASE_URI=postgresql://{username}:{password}@db:{port}/{db_name}
APP_SETTINGS=application.config.DevelopmentConfig
```
