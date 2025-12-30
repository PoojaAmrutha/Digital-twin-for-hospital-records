---
description: Manual Verification of Digital Twin Flow
---

1. **Start the Server** (see start_backend.md).
2. **Open Swagger UI**: Go to `http://127.0.0.1:8000/docs` in your browser.

3. **Create a Doctor**:
   - Expand `POST /users/`.
   - Click "Try it out".
   - JSON:
     ```json
     {
       "name": "Dr. House",
       "email": "house@hospital.com",
       "age": 45,
       "gender": "M",
       "user_type": "doctor"
     }
     ```
   - Execute. Copy the `id` (likely `1`).

4. **Create a Patient**:
   - JSON:
     ```json
     {
       "name": "John Doe",
       "email": "john@example.com",
       "age": 30,
       "gender": "M",
       "user_type": "patient"
     }
     ```
   - Execute. Copy the `id` (likely `2`).

5. **Create a Medical Record**:
   - Expand `POST /medical-records/`.
   - Set `current_user_id` to the Doctor's ID (`1`).
   - JSON:
     ```json
     {
       "record_type": "note",
       "content": "Patient complains of excessive thirst and fatigue. Possible diabetes.",
       "user_id": 2
     }
     ```
   - Execute.

6. **View Digital Twin**:
   - Expand `GET /digital-twin/{user_id}`.
   - Set `user_id` to the Patient's ID (`2`).
   - Execute.
   - Verify that the response includes the **Risk Assessment** and the **Extracted Entities** (Diabetes).
