# Swiss Tournament Database

###Description
Database schema that stores game matches between players. A Python modules ranks the players and pairs them up in matches for a tournament.

###Installation Notes
Install Vagrant and VirtualBox

Clone the repository and cd into the vagrant folder and type `vagrant up` then `vagrant ssh`
Type `cd /vagrant/tournament` and then `python tournament_tests.py` to start the tests.

If the database does not yet exist, type `psql` to enter the PostgreSQL CLI, then type `create database tournament;`

###Technologies
...Python
...PostgreSQL
...Vagrant