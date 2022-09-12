# JWT-login-history
## How to Install
1) Make sure you're using Python 3.10.
2) Use the `pip install -r /path/to/requirements.txt` command in the project folder and all dependancies should be installed.
3) Make sure that you have schema on a running instance of PostgreSQL with name of 'ycp' that can be accessed with the username 'postgres' and the password 'supersecretpassword'.
4) A Postman Collection is available to be used as a reference for sending requests.

## Performance
This application works well for testing environments although it has not been proven in production environments.

## Ideas to make more scalable
Better to use a database type that is well suited for logging, using NoSQL is a possible option.

## Soring options
Ad of now, the data is stored using a PostgreSQL solution as the author did not see the reason for using other database solutions.
