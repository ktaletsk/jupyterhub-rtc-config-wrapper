# jupyterhub-rtc-config-wrapper
Example JupyterHub deployment with granular RTC sharing permissions

## Demo

## Motivation

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

I am really hoping that Groups API will be implemented soon, but until then we can use this workaround and start experimenting with collaboration features on JupyterHub.

To help users to manage RTC permission, I also created JupyterLab extension [jupyterlab-rtc-hub-settings](https://pypi.org/project/jupyterlab-rtc-hub-settings/) which provides UI for managing `server_sharing_{user}` group.

## Installation instructions

Clone this repository:
```bash
git clone https://github.com/ktaletsk/jupyterhub-rtc-config-wrapper.git
```

Install dependencies into separate Conda environment:
```
cd jupyterhub-rtc-config-wrapper
conda env create -n jupyterhub-rtc --file environment.yml
export JUPYTERHUB_WRAPPER_SERVICE_TOKEN=$(openssl rand -hex 32)
```

## Run instructions

```bash
conda activate jupyterhub-rtc
python config-wrapper.py
```

Log in as multiple different users at [127.0.0.1:8989](127.0.0.1:8989). After new users logged in for the first time, the Hub should restart within a minute (configurable duration).

After restart, go to Sharing Settings panel on the left and click on checkbox next to the user with which you would like to share the notebook. Then, open the notebook you would to share, click Share in the main menu and generate a sharable link which you can now send to your collaborator. After they authenticate with *their* Juputerhub credentials, they will be able to view and edit the same notebook in the real time.


## Details on managing groups by API calls

Details below are for manual editing of the sharing groups through API calls. This is not necessary anymore if you use the [jupyterlab-rtc-hub-settings](https://pypi.org/project/jupyterlab-rtc-hub-settings/) extension as it does that for you.

Sharing groups are empty by default. The idea is that users will decide who to share their server with. All they need to do for that is to send a POST API request to Hub's API `/hub/api/groups/server_sharing_<username>/users` with body {'users': '<username_to_share_with>'}. Importantly, <username_to_share_with> should already exist in the system, so should have logged in at least once before.

After making the request, the <username> can now share the notebook link with <username_to_share_with> and they will be able to edit it collaboratively.

To check the groups created in JupyterHub, you can run the following request:

```bash
curl -i -H "Authorization: token <token>"  http://127.0.0.1:8081/hub/api/groups
```

To add new user to group, run 
```bash
curl -i -X POST -H "Content-Type: application/json" -H "Authorization: token <token>" -d '{"users": ["<username_to_share_with>"]}' http://127.0.0.1:8081/hub/api/groups/server_sharing_<username>/users
```