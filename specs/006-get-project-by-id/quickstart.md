# Quickstart validation for get-project-by-id

Prerequisites

- Local application running and connected to the test database
- At least one Project record in the database with known id and is_public true

Validation steps

1. Request public project:
   - curl -sS "http://localhost:9600/api/v1/projects/<PUBLIC_ID>" -v
   - Expect HTTP 200 and JSON body containing id, name, description, owner_id, created_at

2. Request private project without auth:
   - curl -sS "http://localhost:9600/api/v1/projects/<PRIVATE_ID>" -v
   - Expect HTTP 401

3. Request private project with authenticated user lacking permission:
   - curl -sS -H "Authorization: Bearer <TOKEN_WITHOUT_PERMISSION>" "http://localhost:9600/api/v1/projects/<PRIVATE_ID>" -v
   - Expect HTTP 403

4. Request non-existing project:
   - curl -sS "http://localhost:9600/api/v1/projects/<NON_EXISTENT_ID>" -v
   - Expect HTTP 404

5. Request with invalid id format:
   - curl -sS "http://localhost:9600/api/v1/projects/invalid-id" -v
   - Expect HTTP 400

Notes

- Adjust endpoints if route namespace differs. These commands verify end-to-end behavior without prescribing implementation details.
