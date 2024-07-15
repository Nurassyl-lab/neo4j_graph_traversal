# Precautions
- Do not run neo4j server and neo4j desktop at the same time
  - The desktop version is unnecessary
- Check if server is running using `sudo neo4j status`

# How to change config file for neo4j
`sudo vim /etc/neo4j/neo4j.conf`

change this line (below)

`initial.dbms.default_database=freebase-wiki` (write a name for your database instead of freebase_wiki)

by default neo4j server will run neo4j database

# To load the database into a server, load the database from a `.dump` file
`sudo neo4j-admin database load --from-path=/path/to/dump/ <database> --overwrite-destination=true`

i.e., `sudo neo4j-admin database load --from-path=/home/lab716a/Downloads/ freebase-wiki --overwrite-destination=true` (write a name for your database instead of freebase_wiki and --from-path to its location)

# See all database info
`sudo neo4j-admin database info`

If you have loaded the database using previous command the name of the database should appear in the list

# Start or stop commands
* `sudo neo4j start`
* `sudo neo4j stop`
