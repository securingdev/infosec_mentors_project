# The InfoSec Mentors Project
Building a community for those that both seek out and provide mentorship in
Information Security.  Located at [infosecmentors.net](https://infosecmentors.net/).

## Mission Statement:
It is the mission of the InfoSec Mentors Project to provide a platform through
which individuals might more easily obtain, and provide, mentorship within the
Information Security community. Our goal is to help connect those seeking to
develop new skills with those willing to share their experience. To that end,
we ask that members of our community be open to both obtaining and providing 
mentorship when registering to use the platform we have built. It is our sincere
hope that all those who participate in this community obtain as much wisdom as
can be found - while also sharing that wisdom with others. 

## Contributing to the Project

If you would like to contribute to this project, we ask that you please adhere
to Vincent Driessen's [Git Branching model](http://nvie.com/posts/a-successful-git-branching-model/), whereby you submit a pull request for your feature branch so that it 
can be tested before being merged into Development, and then finally into Master.

#### Tabs or Spaces?

This project uses 4 spaces for indentation; Or as I like to think of it - tabs
represented as 4 spaces.

#### Submitting Feedback

Admittedly, this is my first foray into managing an open source project - so I
welcome any and all feedback from the community. I have created a project here
on Github dedicated to channeling Feedback through the development process. As
such, I would ask that you please submit an issue ticket with your feedback so
that it can be tracked, and if appropriate, turned into a ticket for the
"Roadmap" or "Bug Fixes" projects. If you don't want to submit your feedback
publicly, then I encourage you to message me directly on
[Twitter](https://www.twitter.com/andMYhacks).

## Vagrant Setup

The project includes a flask management script for initializing a development database and running the application server.
However, before this can be used a set of environment variables need to be created. These environment variables can either be created
through the shell or stored in the project root directory in a .env file. The project repository includes a .env-example file that
can be used for this purpose. 

    infosec-mentor-project$ cp .env-example .env
    
Modify the .env file to include values relevant to your environment. This file should not be checked into source control and is in the
.gitignore list.

Once the environment variables are updated, you can now initialize the database and run the server.

    infosec-mentor-project$ python manage.py initdb
    Database initialized
    infosec-mentor-project$ python manage.py runserver
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
   
Open a web browser and point it to http://localhost:5000

### Running With Vagrant

From the root of the project folder:
    
    infosec-mentor-project$ vagrant up
    ...
    ...
    ==> default:  * Restarting app server(s) uwsgi
    ==> default:    ...done.
    ==> default:  * Restarting app server(s) uwsgi
    ==> default:    ...done.
    ==> default: Database initialized
    infosec-mentor-project$ 
    
Open a web browser and point it to http://localhost:8000
