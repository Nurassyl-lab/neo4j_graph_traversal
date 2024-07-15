# Installation
## Installing Neo4j Server (Linux)
Follow the instructions in [Neo4j](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/)

## Installing Neo4j Desktop
Follow the instructions in [Neo4j](https://neo4j.com/docs/desktop-manual/current/installation/download-installation/).
- Do note that the desktop edition is unnecessary if you have the server, but the desktop allows you to use various projects.

## Precautions
- Neo4j server only contains one project instance (DBMS), so you would have to [load separate databases](#loading-a-database)
- Do not run neo4j server and neo4j desktop at the same time
- Check if server is running using `sudo neo4j status`

&nbsp;

# Loading a database
## Load into Server
To load database into a server, load the database from a `.dump` file with the following command:
`sudo neo4j-admin database load --from-path=/path/to/dump/ <database> --overwrite-destination=true`

i.e., 

`sudo neo4j-admin database load --from-path=/home/lab716a/Downloads/ freebase-wiki --overwrite-destination=true` (write a name for your database instead of freebase_wiki and --from-path to its location)

## Add the Database
Add the database into the config file for neo4j with the following command:
`sudo vim /etc/neo4j/neo4j.conf`

change this line (below)

`initial.dbms.default_database=freebase-wiki` (write a name for your database instead of freebase_wiki)

by default neo4j server will run neo4j database

&nbsp;

# Neo4j Commands
## Start Neo4j
The following command will start the server if it is not running.

`sudo neo4j start`

## Stop Neo4j
The following command will stop the server if it is running.

`sudo neo4j stop`

## Check Neo4j Server Status
The following command will tell you if the server is running or not: 

`sudo neo4j status`

## See all database info
`sudo neo4j-admin database info`

If you have loaded the database using [previous command](#add-the-database) the name of the database should appear in the list

## Visualize Neo4j in the Server
After [starting neo4j](#start-neo4j), open the browser with the following command

`http://localhost:<server-port>/browser/`

where `<server-port>` is the designed port by neo4j.

## Visualize Neo4j in your Local PC
From ssh terminal, run the following command:

`ssh <server-name> -L <server-port>:localhost:<server-port> -L <computer-port>:localhost:<computer-port>`

where `<server-name>` is refers the connection name to the computer running the server, `<server-port>` the port number neo4j is hosting the graph, by default it is `7474`, and `<computer-port>` your desired local port. 

i.e.,

`ssh lab-server -L 7474:localhost:7474 -L 7687:localhost:7687`

and then follow command as [before](#visualize-neo4j-in-the-server)
