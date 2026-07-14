# Tomeys Frontend Context

## Stack
Backend:
- FastAPI
- SQLAlchemy
- SQLite

Frontend goals:
- User dashboard
- Club discovery
- Club pages
- Reading progress

# Tomeys API

## Authentication

POST /auth/login
- Email/password login
- Returns Tomeys JWT

POST /auth/google
- Google OAuth login
- Returns Tomeys JWT


## User

GET /users/me
- Current user profile

POST /users/
- Create account


## Dashboard

GET /dashboard
- Personal dashboard

Returns:
- current readings
- clubs
- active cycles
- history
- notes


## Clubs

POST /clubs/
- Create club

GET /clubs/
- Current user's clubs

GET /clubs/discover
- Public clubs

GET /clubs/search?q=
- Search public clubs

GET /clubs/{club_id}/members
- Club members

GET /clubs/{club_id}/dashboard
- Club dashboard


## Voting Cycles

POST /clubs/{club_id}/cycles
- Create cycle

GET /clubs/{club_id}/cycles/active
- Current cycle

POST /clubs/cycles/{cycle_id}/close

POST /clubs/cycles/{cycle_id}/winner


## Suggestions

POST /clubs/{club_id}/suggestions
- Suggest book

GET /clubs/{club_id}/suggestions
- View suggestions


## Voting

POST /votes/{suggestion_id}
- Vote

DELETE /votes/{suggestion_id}
- Remove vote


## Reading

(Current/future)
- reading progress
- notes
- reviews
