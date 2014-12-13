ruitknocks
==========

A "Knocks" system, specifically adapted for Beirut

To setup (more details are forthcoming):

Install python 2.7 (or higher version)
Install virtualenv

Activate virtualenv in the ruitknocks directory

Run pip-install flask once in virtualenv

Run sudo python RuitKnocks.py

Option Flags:

-d opens in debug mode. This will not send text messages and will write to a temporary database (a copy of the original database)
Allows new endpoints:
/clearKnocks - Clears ALL knocks from the database
/clearAll - Clears ALL tables except carriers
/setup - Creates a new .db file. Will fail if the file already exists and has tables in it

-n opens in new mode. Currently used with __newTables to test new features