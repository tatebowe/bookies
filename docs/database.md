User
----
- id
- username
- email
- password_hash
- created_at


Club
----
- id
- name
- description
- invite_code
- owner_id
- created_at

ClubMember
----------
id
user_id
club_id
role
joined_at

Book
----
- id
- title
- author
- isbn
- description
- pages
- created_at

MonthlyBook
-----------
- id
- club_id
- book_id
- month
- year

ReadingStatus
-------------
- id
- user_id
- monthly_book_id
- status
- updated_at

Suggestion
----------
- id
- club_id
- book_id
- submitted_by
- created_at

Vote
----
- id
- suggestion_id
- user_id
- created_at

