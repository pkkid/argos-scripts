# Useful Argos Scripts
Useful scripts to run in Argos or Bitbar.

* `bitbucket.1c.300s+.py` - Displays Bitbucket pull requests in the system tray.
* `jira.1c.300s+.py` - Displays open JIRA issues in the system tray.
* `virt-manager.1c.60s+.py` - Allows you to manage virt-manager VMs from the system tray.
* `radio.1c.3s+.py` - Simple internet radio player in the system try.

### Installation

1. You can install Argos from the gnome-extensions website.
2. Install requirements: `sudo -H pip3 install PIL requests`
3. Copy and paste these scripts `~/.config/argos/` and make them executable.
4. If using the radio script, you need vlc installed and on the system path.
5. If using the Bitbucket or Jira scripts, add a configuration file at `~/.config/atlassian.json`.

```json
{
  "jira": {
    "host": "https://example.atlassian.net",
    "auth": "user@example.com:ke4xExampleToken96C",
    "team_filter": "12345"
  },
  "bitbucket": {
    "host": "https://git.example.net",
    "auth": "username:MTg4MxExampleTokenTLE6"
  }  
}
