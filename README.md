# Book Reservation System

## 1. Overview
This project is a **Book Reservation System** implemented using **FastAPI**, **SQLAlchemy**, **Alembic**, **MongoDB** and **Redis** follows principles of **Domain-Driven Design (DDD)**, **CQRS (Command Query Responsibility Segregation)**, and **Event-Driven Architecture**. The system allows users to register, browse books, make reservations, and manage user data efficiently with an event-driven architecture that process events asynchronously using RabbitMQ.

## Features
- User authentication and management
- Book catalog with search functionality
- Reservation system with status tracking
- Role-based access control (Admin, Author, Customer)
- Caching with Redis for improved performance
- Asynchronous database operations using SQLAlchemy
- Database migrations handled by Alembic
- MongoDB integration for book-related metadata

## 2. Tech Stack
- **FastAPI** for API development
- **SQLAlchemy** for PostgreSQL database management
- **Redis** for caching and OTP management
- **RabbitMQ** for event-driven message processing
- **MongoDB** for NoSQL storage of book metadata

- **Alembic** for database migrations
- **Docker** for containerized deployment
- **Pydantic** for data validation and serialization
- **Docker** Containerization for easy deployment

## 3. Architecture
This system is designed based on **CQRS & DDD**, with clear separation of **Commands, Queries, and Events**.
- **Commands** handle data modifications (e.g., creating a reservation)
- **Queries** fetch data (e.g., retrieving book details)
- **Events** handle background tasks (e.g., sending reminders)

### 3.1 Layers
- **Domain Layer**: Business logic & entity definitions
- **Application Layer**: Service classes managing use cases
- **Infrastructure Layer**: Database interactions (SQLAlchemy, Redis, RabbitMQ, MongoDB)
- **Presentation Layer**: FastAPI routes (controllers)
- **Messaging Layer**: Handles asynchronous communication via RabbitMQ

## 4. Database Models
### 4.1 User Model
- `id`: Unique identifier
- `username`: Unique username
- `email`: Email address
- `password`: Hashed password
- `role`: User role (admin, customer, author)
- `is_active`: Status flag

### 4.2 Book Model
- `id`: Unique identifier
- `title`: Book title
- `isbn`: Unique ISBN
- `price`: Book price
- `genre_id`: Associated genre
- `description`: Book description
- `units`: Total stock
- `reserved_units`: Reserved stock
- `authors`: List of associated authors

### 4.3 Reservation Model
- `id`: Unique identifier
- `customer_id`: Associated customer
- `book_id`: Reserved book
- `start_of_reservation`: Start date
- `end_of_reservation`: End date
- `price`: Reservation price
- `status`: Reservation status (pending, active, completed)
- `queue_position`: Position in queue if waiting

## Event-Driven Messaging
- **RabbitMQ** is used to handle event-based communication:
  - `book_created`
  - `book_updated`
  - `book_deleted`
  - `reservation_created`
  - `reservation_ends_soon`
  - `otp_generated`

## Caching with Redis
- Book data is cached to reduce DB queries
- OTPs are stored with expiration time for authentication
- User session management for quick authentication validation

## Security & Authentication
- OAuth2 password flow for authentication
- Role-based access control for different operations
- Rate-limiting for OTP generation (5 attempts in 2 minutes, 10 in an hour)

## Deployment
- Dockerized setup with separate services for PostgreSQL, Redis, RabbitMQ, and MongoDB
- `docker-compose.yml` for easy container management
- Environment variables for configuration management

---
## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.10+
- PostgreSQL
- Redis
- RabbitMQ
- MongoDB
- Docker (optional, for containerized deployment)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo.git .
   ```
2. Create a virtual environment and activate it:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```sh
   alembic upgrade head
   ```
5. Run the application:
   ```sh
   uvicorn app.main:app --reload
   ```

## Usage
### Running with Docker
1. Build and start the services:
   ```sh
   docker-compose up --build
   ```
2. Access the API at:
   ```sh
   http://localhost:8000/docs
   ```

## API Endpoints
| Method |                 Endpoint                 |               Description             |
|--------|------------------------------------------|---------------------------------------|
| POST   | `/auth/signup/`                          | Register a new user                   |
| POST   | `/auth/login/`                           | Authenticate user and get access token|
| POST   | `/auth/logout/`                          | Logout user                           |
| POST   | `/books/`                                | Create a new book                     |
| GET    | `/books/`                                | Get list of books                     |
| GET    | `/books/{id}`                            | Get book details                      |
| PATCH  | `/books/{id}`                            | Update a book                         |
| DELETE | `/books/{id}`                            | Delete a book                         |
| POST   | `/customer/`                             | Create a new customer                 |
| GET    | `/customer/`                             | Get list of customers                 |
| GET    | `/customer/{id}`                         | Get customer details                  |
| PATCH  | `/customer/{id}`                         | Update a customer                     |
| DELETE | `/customer/{id}`                         | Delete a customer                     |
| POST   | `/reservations/`                         | Create a reservation                  |
| DELETE | `/reservations/cancel/{reservation_id}/` | Create a reservation                  |

## Environment Variables
Create a `.env` file and add:
```env
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/"

SECRET_KEY="your-secret-key-here"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB0=0
REDIS_DB1=1
REDIS_DB2=2

POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db2

MONGO_USER=user
MONGO_PASSWORD=password

RABBITMQ_USER="guest"
RABBITMQ_PASSWORD="guest"
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature-name`)
5. Open a Pull Request

## License
This project is licensed under the MIT License.

