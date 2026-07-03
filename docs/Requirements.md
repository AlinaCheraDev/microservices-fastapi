Existing requirements
1. Pets API
  1. Create Pet
  2. Update Pet 
  3. Delete Pet (Destroy)
  4. Get One Pet By Id
  5. List Pets
2. Admin API
  1. Create account
  2. Update account
  3. Delete account
  4. Get one account by id
  5. Account types: User, Admin
3. Authorization API
  1. Login into account
  2. Register a new account

New requirements
1. Add logging
2. Add global exception handling
3. Add type hints
4. Add docstrings
5. Add unit tests
6. Add API versioning
7. Add database connection pooling (in functie de setare: pool sau single client)
8. Add caching (in functie de setare: redis sau in-memory)
9. Add soft deletes for all entities
10. Add contraints for age field min = 0, max = database integer max
11. Add input validation
12. Add pagination
13. Replace magic strings with constants
14. Set DEBUG value based on ENVIRONMENT env value
15. Set CORS
16. A user cannot delete / update a pet which they do not own
17. A pet should by unique by name, user and type
18. A pet can be set private / public by the owner (default is private)
19. A user can only see public pets or pets they own
20. Add the possiblity to filter for pets search by name, type or owner (email)
21. Add password recovery