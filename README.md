# Useful Argos Scripts
Useful scripts to run in Argos or Bitbar.

* `bitbucket.1c.300s+.py` - Displays Bitbucket pull requests in the system tray.
* `jira.1c.300s+.py` - Displays open JIRA issues in the system tray.
* `virt-manager.1c.60s+.py` - Allows you to manage virt-manager VMs from the system tray.
* `radio.1c.3s+.py` - Simple internet radio player in the system try.

### Installation
1. You can install Argos from the gnome-extensions website.
2. Copy and paste these scripts `~/.config/argos/` and make them executable.
3. If using the Bitbucket script, add your auth info to your .bash_profile.
   <br/>`export JIRA_HOST="https://jirahost.com"`
   <br/>`export JIRA_AUTH="email:token"`
4. If using the JIRA script, add your auth info to your .bash_profile.
   <br/>`export BITBUCKET_HOST="https://bitbuckethost.com"`
   <br/>`export BITBUCKET_AUTH="username:token"`
5. If using the radio script, you need vlc installed and on the system path.
6. Enjoy.
