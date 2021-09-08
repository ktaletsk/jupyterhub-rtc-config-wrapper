# Configuration file for jupyterhub.
import os
import pickle


# Insecure! Dummy authenticator accepts any password
c.JupyterHub.authenticator_class = 'dummy'

# Leave user servers running when restarting the hub
c.JupyterHub.cleanup_servers = False

# Specific to my computer configuration, can be changed
c.JupyterHub.port = 8989

# Read the backed up users and groups
try:
  infile = open('users.pkl','rb')
  users = pickle.load(infile)
  infile.close()
except:
  users = []

try:
  infile = open('groups.pkl','rb')
  groups_backup = pickle.load(infile)
  infile.close()
except:
  groups_backup = {}


# Create server sharing groups and roles
groups = {}
roles = []

for user in users:
    group = {f'server_sharing_{user}': groups_backup.get(f'server_sharing_{user}', [])}
    groups.update(group)

    sharing_role = {
        'name': f'server_sharing_{user}_role',
        'description': f'Server sharing of {user}',
        'scopes': [f'access:servers!user={user}'],
        'groups': [f'server_sharing_{user}']
    }

    sharing_group_editing_role = {
        'name': f'server_sharing_{user}_group_editing_role',
        'description': f'Edit server_sharing_{user} group',
        'scopes': [f'groups!group=server_sharing_{user}'],
        'users': [f'{user}']
    }

    usernames_reading_role = {
        'name': f'usernames_reading_{user}_role',
        'description': 'Usernames reading group',
        'scopes': ['read:users:name'],
        'users': [f'{user}']
    }

    roles.append(sharing_role)
    roles.append(sharing_group_editing_role)
    roles.append(usernames_reading_role)

roles.append({
   'name': 'server',
   'scopes': ['all'],
 })

c.JupyterHub.load_groups = groups
c.JupyterHub.load_roles = roles

# Insecure! just for easy testing
c.JupyterHub.spawner_class = 'simple'

# singleuser-server: jupyterlab with rtc enabled
c.Spawner.cmd = ['jupyter-labhub']
c.Spawner.args = ['--collaborative']


# Debug logging
c.Application.log_level = 'DEBUG'
c.Spawner.debug = True

# Create admin token for checking for new users
c.JupyterHub.services = [
  {
    "name": "service-token",
    "admin": True,
    "api_token": os.getenv('JUPYTERHUB_WRAPPER_SERVICE_TOKEN'),
  },
]