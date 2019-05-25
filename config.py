import hashlib
# secret key for flask app. This should not be known to others.
secret_key = hashlib.sha256(b'very secure secret key').hexdigest()

# path where db file will be saved. folder should exist.
dbpath = 'db/sumango3ctf.db'

# salt used for making hash of password
member_salt = 'this is salt for hashing password of members'

# salt used for making hash of flag
quiz_salt = 'this is salt for hashing flag of quizs'

# member signed in with this key will get admin level auth (2)
admin_key = 'this is key for admin'

# member signed in with this key will get member level auth (1)
member_key = 'this is key for member'

# bonus point for first solver
bonus = 10
