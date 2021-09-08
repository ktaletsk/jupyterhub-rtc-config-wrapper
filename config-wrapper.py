import os
import asyncio
import requests
import pickle

api_url = 'http://127.0.0.1:8081/hub/api/'
token = os.getenv('JUPYTERHUB_WRAPPER_SERVICE_TOKEN')
usernames_memory = set()

def check_if_users_changed_and_backup():
    global usernames_memory
    r = requests.get(api_url + 'users', headers={'Authorization': 'token %s' % token})

    if r.status_code == 200:
        usernames = set(map(lambda x: x['name'], r.json()))
        if usernames != usernames_memory:
            usernames_memory = usernames
            
            # Updated pickled users
            outfile = open('users.pkl','wb')
            pickle.dump(list(usernames_memory), outfile)
            outfile.close()
            
            return True
    return False

def backup_groups():
    # JupyterHub RBAC group members can be updated with API call
    # https://jupyterhub.readthedocs.io/en/rbac/_static/rest-api/index.html#path--groups--name--users
    # After restarting JupyterHub, updated groups will be lost
    # Therefore, we need to back up any changes to groups made in the runtime
    # and restore them after restarting JupyterHub
    r = requests.get(api_url + 'groups', headers={'Authorization': 'token %s' % token})
    if r.status_code == 200:
        groups = r.json()
        groups_backup = {}

        for group in groups:
            groups_backup[group['name']] = group['users']

        outfile = open('groups.pkl','wb')
        pickle.dump(groups_backup, outfile)
        outfile.close()

async def jupyterhub_task():
  proc = await asyncio.create_subprocess_exec('jupyterhub', '--config', 'jupyterhub_config.py')
  try:
    return await proc.communicate()
  except asyncio.CancelledError:
    print('Terminating process')
    proc.terminate()

    # Wait for termination to complete
    await proc.communicate()

async def main():
  i = 0
  while True:
    task = asyncio.create_task(jupyterhub_task())
    
    # Check if users have changed
    while True:
      # Check every 10 seconds
      await asyncio.sleep(60)

      backup_groups()
      # Check if users have changed
      if check_if_users_changed_and_backup():
        print('Users changed')
        break

    task.cancel()
    await task
    i += 1

asyncio.run(main())