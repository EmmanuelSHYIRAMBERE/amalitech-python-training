# Explanation of the URL Shortener Microservice Project

## **Database Queries**

The application interacts with a PostgreSQL database to store and retrieve URL data. Below is an explanation of the database queries used in the project:

### **Sample Query: Storing a Shortened URL**
```python
from django.db import models

class URL(models.Model):
    short_code = models.CharField(max_length=10, unique=True)
    original_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

# Saving a new URL
url = URL(short_code="abc123", original_url="https://example.com")
url.save()
```
#### **Explanation**:
1. **`short_code`**: A unique identifier for the shortened URL.
2. **`original_url`**: The full URL provided by the user.
3. **`created_at`**: Automatically stores the timestamp when the URL is created.
4. **`url.save()`**: Executes an `INSERT` query to store the data in the database.

### **Sample Query: Retrieving a URL**
```python
short_code = "abc123"
url = URL.objects.get(short_code=short_code)
print(url.original_url)
```
#### **Explanation**:
1. **`URL.objects.get(short_code=short_code)`**: Executes a `SELECT` query to fetch the row where `short_code` matches.
2. **`print(url.original_url)`**: Outputs the original URL.

---

## **Docker and Docker Compose**

### **What is Docker?**
Docker is a platform that allows developers to package applications and their dependencies into lightweight, portable containers. These containers can run consistently across different environments.

### **What is Docker Compose?**
Docker Compose is a tool for defining and running multi-container Docker applications. It uses a `docker-compose.yml` file to configure the services, networks, and volumes required for the application.

### **Why Use Both Dockerfile and docker-compose.yml?**
- **Dockerfile**: Defines how to build the application image.
- **docker-compose.yml**: Orchestrates multiple containers (e.g., web and database).
- **Why Not One?**: Using both separates concerns. The Dockerfile focuses on the application, while docker-compose.yml manages the environment.

### **Dockerfile Explanation**
```dockerfile
# Stage 1: builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```
#### **Line-by-Line Explanation**:
1. **`FROM python:3.11-slim AS builder`**: Uses a lightweight Python image as the base for the build stage.
2. **`WORKDIR /app`**: Sets the working directory inside the container.
3. **`COPY requirements.txt .`**: Copies the `requirements.txt` file into the container.
4. **`RUN pip install --upgrade pip && \`**: Upgrades `pip`.
5. **`pip install --no-cache-dir --prefix=/install -r requirements.txt`**: Installs dependencies without caching.
6. **`FROM python:3.11-slim`**: Starts a new stage for the runtime environment.
7. **`COPY --from=builder /install /usr/local`**: Copies dependencies from the build stage.
8. **`COPY . .`**: Copies the application code.
9. **`ENV PYTHONDONTWRITEBYTECODE=1 \`**: Prevents Python from writing `.pyc` files.
10. **`PYTHONUNBUFFERED=1`**: Ensures logs are output immediately.
11. **`EXPOSE 8000`**: Exposes port 8000.
12. **`CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]`**: Starts the application using Gunicorn.

### **docker-compose.yml Explanation**
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME:-urlshortener}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5435:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 5s
      retries: 5

  web:
    build: .
    command: >
      sh -c "python manage.py migrate --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy

volumes:
  pg_data:
```
#### **Line-by-Line Explanation**:
1. **`services:`**: Defines the services in the application.
2. **`db:`**: Configures the PostgreSQL database service.
3. **`image: postgres:15`**: Uses the PostgreSQL 15 image.
4. **`environment:`**: Sets environment variables for the database.
5. **`ports:`**: Maps port 5435 on the host to 5432 in the container.
6. **`volumes:`**: Persists database data.
7. **`healthcheck:`**: Checks if the database is ready.
8. **`web:`**: Configures the web service.
9. **`build: .`**: Builds the Docker image from the current directory.
10. **`command:`**: Runs migration and starts the application.
11. **`volumes:`**: Mounts the current directory.
12. **`ports:`**: Maps port 8000.
13. **`env_file:`**: Loads environment variables from `.env`.
14. **`depends_on:`**: Ensures the database is ready before starting the web service.
15. **`volumes:`**: Defines named volumes.

---

## **Protocols, ABCs, Async/Await, Dataclasses, Regex, Typing, Environment Variables**

### **Protocols**
- **Definition**: Protocols define contracts for components, ensuring that classes implementing the protocol adhere to a specific structure.
- **Usage in Project**: Protocols can be used to define contracts for URL shortening services or storage backends.
- **Code Example**:
```python
from typing import Protocol

# Define a protocol for URL shortening services
class URLShortenerProtocol(Protocol):
    def shorten_url(self, original_url: str) -> str:
        """Shortens the given URL and returns the short code."""
        ...

    def expand_url(self, short_code: str) -> str:
        """Expands the short code back to the original URL."""
        ...

# Implement the protocol in a concrete class
class URLShortener(URLShortenerProtocol):
    def shorten_url(self, original_url: str) -> str:
        return "abc123"  # Example short code

    def expand_url(self, short_code: str) -> str:
        return "https://example.com"  # Example original URL
```
- **Impact if Not Used**: Without protocols, the code becomes tightly coupled, making it harder to swap implementations.

### **Abstract Base Classes (ABCs)**
- **Definition**: Abstract Base Classes enforce consistent implementation by defining abstract methods.
- **Usage in Project**: ABCs can be used to define a base class for storage backends (e.g., database, cache).
- **Code Example**:
```python
from abc import ABC, abstractmethod

# Define an abstract base class for storage backends
class StorageBackend(ABC):
    @abstractmethod
    def save_url(self, short_code: str, original_url: str):
        """Saves the short code and original URL to the storage backend."""
        pass

    @abstractmethod
    def get_url(self, short_code: str) -> str:
        """Retrieves the original URL for the given short code."""
        pass

# Implement the abstract base class for a database storage backend
class DatabaseStorage(StorageBackend):
    def save_url(self, short_code: str, original_url: str):
        print(f"Saving {short_code} -> {original_url} to database")

    def get_url(self, short_code: str) -> str:
        return "https://example.com"  # Example original URL
```
- **Impact if Not Used**: Without ABCs, there is no enforced structure, leading to inconsistent implementations.

### **Async/Await**
- **Definition**: Async/Await enables asynchronous programming, improving scalability for I/O-bound tasks.
- **Usage in Project**: Async can be used for database queries or external API calls.
- **Code Example**:
```python
import asyncio

# Simulate an asynchronous function to fetch a URL
async def fetch_url(short_code: str) -> str:
    await asyncio.sleep(1)  # Simulate I/O operation
    return "https://example.com"  # Example original URL

# Main coroutine to demonstrate async/await usage
async def main():
    url = await fetch_url("abc123")
    print(url)

# Run the main coroutine
asyncio.run(main())
```
- **Impact if Not Used**: Without async, blocking operations can reduce performance and scalability.

### **Dataclasses**
- **Definition**: Dataclasses simplify class definitions by automatically generating methods like `__init__` and `__repr__`.
- **Usage in Project**: Dataclasses can be used for models like URL data.
- **Code Example**:
```python
from dataclasses import dataclass

# Define a dataclass for URL data
@dataclass
class URL:
    short_code: str  # The short code for the URL
    original_url: str  # The original URL
    created_at: str  # The creation timestamp

# Create an instance of the URL dataclass
url = URL(short_code="abc123", original_url="https://example.com", created_at="2026-04-22")
print(url)
```
- **Impact if Not Used**: Without dataclasses, class definitions become verbose and harder to maintain.

### **Regular Expressions (Regex)**
- **Definition**: Regex is used for pattern matching in strings.
- **Usage in Project**: Regex can validate URLs.
- **Code Example**:
```python
import re

# Define a regex pattern for validating URLs
URL_REGEX = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")

# Function to validate a URL using the regex pattern
def is_valid_url(url: str) -> bool:
    return bool(URL_REGEX.match(url))

# Test the function with valid and invalid URLs
print(is_valid_url("https://example.com"))  # True
print(is_valid_url("invalid-url"))  # False
```
- **Impact if Not Used**: Without regex, string validation becomes error-prone and less efficient.

### **Typing**
- **Definition**: Typing adds type hints, improving code clarity and enabling static analysis.
- **Usage in Project**: Typing can be used for function signatures and class attributes.
- **Code Example**:
```python
from typing import TypedDict

# Define a TypedDict for URL data
class URLData(TypedDict):
    short_code: str  # The short code for the URL
    original_url: str  # The original URL

# Create an instance of the TypedDict
url_data: URLData = {"short_code": "abc123", "original_url": "https://example.com"}
print(url_data)
```
- **Impact if Not Used**: Without typing, debugging becomes harder, and code is less self-documenting.

### **Environment Variables**
- **Definition**: Environment variables store sensitive data like credentials.
- **Usage in Project**: Environment variables are used for database credentials and secret keys.
- **Code Example**:
```python
from decouple import config

# Load environment variables using python-decouple
DB_NAME = config("DB_NAME", default="urlshortener")  # Database name
DB_USER = config("DB_USER", default="postgres")  # Database user

# Print the loaded environment variables
print(f"Connecting to database {DB_NAME} as user {DB_USER}")
```
- **Impact if Not Used**: Without environment variables, sensitive data may be hardcoded, leading to security risks.

---

Would you like further details or edits?