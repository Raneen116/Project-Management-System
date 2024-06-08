# Project-Management-System
A project management system where users can create and manage projects, tasks, and milestones

#API endpoints

1. login api -- api/token/
    payload: { "email" : "user email", "password" : "user password" }

2. get all projects -- api/projects/

3. create a new project -- api/projects/
    payload: { "name" : "project name", "description" : "project description", "members": ["user id"]" }

4. update a project -- api/projects/
    payload: { "id": 1, "name" : "project name", "description" : "project description", "members": ["user id"]" }

5. delete a project -- api/projects/?id=1

6. get all tasks -- api/tasks/

7. create a new task -- api/tasks/
    payload: { "project":project id, "name" : "task name", "description" : "task description", "assigned_to": user id, status=status }
    NOT_YET_STARTED = "NOT_YET_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ON_HOLD = "ON_HOLD"

8. update a task -- api/tasks/
        payload: { "id": task id,"project":project id, "name" : "task name", "description" : "task description", "assigned_to": user id, status=status }

9. delete a task -- api/tasks/?id=1


10. get all milestones -- api/milestones/

11. create a new milestone -- api/milestones/
    payload: {"project":project id, "name" : "task name", "description" : "task description" }

12. update a milestone -- api/milestones/
        payload: { "id":milestone id, "project":project id, "name" : "task name", "description" : "task description" }

13. delete a milestone -- api/milestones/?id=1

14. assign task to user -- api/assin-tasks
    payload: { "task":task id,"assigned_to":user id}