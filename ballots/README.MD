# For testing purposes run manage.py runserver in terminal. All migrations should be up to date. Verify that users/migrations are up to date before creating new users.
# Ballot admin processes are managed through the /ballot-admin url. 
# Ballot deletion is only possible through the /admin/ url.
# To run testing suite run manage.py runtests in terminal.

Server may fail to start if database is not set up. Create a db.sqlite3 file and populate using the django admin site. Any data added using admin site can be deleted.
