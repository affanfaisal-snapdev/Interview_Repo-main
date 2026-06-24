# Changes After the First Commit

After the `first commit`, two main updates were added to the project.

## 1. Authentication was added

This update made the app work with users instead of anonymous access.

- Added `/auth/register` so a new user can sign up.
- Added `/auth/login` so an existing user can sign in.
- Passwords are now stored safely as hashed values, not plain text.
- Login now returns a JWT token that is used to access protected endpoints.
- Protected routes support Bearer token authentication through the `Authorization` header.
- A bypass option was added through the `X-Bypass-Key` header for local development/testing.
- Chat and session routes now require an authenticated user.
- Sessions are tied to a specific user, so one user cannot access another user's chat session.

Supporting changes in this update:

- Added a `users` table and related database logic.
- Added auth schemas and an auth service.
- Added new environment settings for JWT and the local bypass key.
- Renamed the `langgraph` package to `chatgraph` for clearer naming.
- Added tests for auth and updated chat/session tests.

## 2. Ecommerce NL-to-SQL support was added

This update made the chatbot able to answer some ecommerce questions from database data.

- Added product and order APIs to list sample ecommerce data.
- Added `products` and `orders` database models and repository logic.
- Added a new `nl_to_sql` service that turns simple product/order questions into SQL.
- The SQL feature is read-only and restricted to safe `SELECT` queries.
- It only allows access to the `products` and `orders` tables.
- If a message is about ecommerce data, the chat flow can answer from the database instead of only using the normal AI response.

Supporting changes in this update:

- Updated the chat workflow to include the ecommerce query path.
- Improved Gemini-related service handling for the new flow.
- Added tests for ecommerce routes and updated chat tests.

## In Short

After the first commit, the project moved from a basic chatbot into:

- a chatbot with user authentication and protected sessions
- a chatbot that can also answer simple ecommerce database questions
