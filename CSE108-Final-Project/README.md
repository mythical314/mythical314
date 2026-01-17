User can add/unadd friends and view friends in the friend list. 
User can challenge a friend to a duel and select one of the quizzes they created. 
The friend can accept or decline the challenge request. 
The duel trivia quiz can be done asynchronously because that's easier. 
But if we have time, we can try synchronously and add a countdown timer. 

user input needs to be sanitized, 
big emphasis on web security

Database :
- only one type of user
- One-to-many relationships : one user can create many quizzes, one quiz has many questions
- Many-to-many relationships : many users have many friends
- One-to-one : one user (challenger) in challenge, one user (opponent) in challenge
- Tables include: users, friendships, quizzes, questions, and challenges (active ones)

Web Hosting done using Vercel

Roles :
- Matthew - Login and Sign out
- Trisha - database setup and admin page
- Julian - friendlist
- Alex - quizzes

Timeline :
- pages, buttons, file structure by Friday
- Data submission done over the weekend

TERMINAL GIT COMMANDS:
1. git checkout -b new-branch-name main        : This creates a new branch from the latest main
2. git add .                                   : This stages all modified files for commit, don't forget the .
3. git commit -m "your commit message"         : This commits the staged change
4. git status                                  : This is optional but it helps so you can check whether you added and committed all changed files
5. git checkout main                           : This switches to main branch
6. git pull origin main                        : This pulls latest changes from main branch
Switch back to your branch and merge main into it. This is to check for any conflicts and to resolve them.
7. git checkout new-branch-name                : This switches back to your branch
8. git merge main                              : This merges main into your branch to check for conflicts
9. git checkout main                           : After resolving conflicts, switch to main
10. git merge new-branch-name                   : Merge your branch into main
11. git branch -d new-branch-name              : This deletes that branch you made
13. git branch                                 : This is optional but it allows to view all branches
14. git push origin main                       : This actually pushes your changes to main and makes those changes visible on github
