# Precautions
- Do not run neo4j server and neo4j desktop at the same time
- check if server is running using `sudo neo4j status`

# how to change config file for neo4j
`sudo vim /etc/neo4j/neo4j.conf`

change this line (below)
`initial.dbms.default_database=freebase-wiki` (write a name of your database insteaf of freebase_wiki)
by default neo4j server will run neo4j database

# to load the database to a server, database is loaded from a `.dump` file
`sudo neo4j-admin database load --from-path=/home/lab716a/Downloads/ freebase-wiki --overwrite-destination=true` (write a name of your database insteaf of freebase_wiki)

# see all database info
`sudo neo4j-admin database info`
if you have kiaded the database using previous command the name of the database should appear in the list


