# jupyterhub-rtc-config-wrapper
Example JupyterHub deployment with auto-generating server sharing permissions

This work is motivated by the need of creating collaborative JupyterHub deployment while not having the list of users in advance. This is often the case in organizations where JupyterHub is configured with OAuthenticator and new users should automatically gain access when joining the organization (and getting the org email).

The initial proof of concept of combining JupyterLab 3.1+ and JupyterHub 2.0 was published earlier https://github.com/manics/jupyterhub-rtc-example. Unfortunately, current JupyterHub 2.0 prerelease does not allow modifying or even viewing RBAC Groups through the API, only from the config file. To help solve that, I created a wrapper that runs JupyterHub as an async task and can restart it when necessary. For purposes of this demo, wrapper is going to continiously check if list of users has changed on JupyterHub using API call, and when that happens, it will restart the JupyterHub. Config file was modified to automatically build the roles and groups for each user in the following format:

```py
c.JupyterHub.load_groups = {
  f'server_sharing_{user}': [],
  ...
}

c.JupyterHub.load_roles = [
  {
    'name': f'server_sharing_{user}_group',
    'description': f'Server sharing of {user}',
    'scopes': [f'access:servers!user={user}'],
    'groups': [f'server_sharing_{user}']
  },
  ...
]
```

I am really hoping that Groups API will be implemented soon, but until then we can use this workaround and start experimenting with collaboration features on JupyterHub

## Run instructions

### Dockerfile

### Locally