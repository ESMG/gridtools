# Jupyter

I currently run a Oracle VirtualBox on a MacOS and have the network setting for
Adapter 1 set as bridged over the wifi interface (en0).  Doing so, I get a DHCP
address for my local network at the same level as the MacOS computer.  This allows
me to use that IP for sharing the jupyter and bokah servers from the VM to a local
browser on the MacOS.   In this documentation, I assume the VM is on the address
192.168.131.54.

Launching a jupyterlab session, I prefer not to have it try and start a browser
from the VM.  The default port is 8888.
```
$ conda activate <env>
(env) $ jupyter lab --ip=192.168.131.54 --no-browser
```

A jupyterlab can be started for each conda enviroment, but do not attempt to
open the same notebook file between two jupyterlab instances.  It will do it,
but will cause odd things to happen.

To enable multiple environments, use separate ports via (--port).  It turns out
jupyterlab is able to figure out other ports are busy and auto increments the
port number.  Specifying the port number is not necessary unless you want it to
be really different.
```
(env) $ jupyter lab --ip=192.168.131.34 --port=8889 --no-browser
```

To test a bokeh application to make sure it can be embedded in a jupyter lab
notebook with working interactive widgets, use this example 
[script](https://github.com/bokeh/bokeh/blob/2.3.0/examples/howto/server_embed/notebook_embed.ipynb).

Using the above default launching of jupyter lab, the last line of the
notebook should read:
```
show(bkapp, notebook_url="http://192.168.131.54:8888")
```

# Jupyter Shortcuts

You can install the shortcuts within JupyterLab web interface through Settings,
Advanced Setting Editor and Keyboard Shortcuts and edit the "User Preferences"
pane.  Or copy "shortcuts.jupyterlab-settings" to:

```text
${HOME}/.jupyter/lab/user-settings/@jupyterlab/shortcuts-extension/shortcuts.jupyterlab-settings
```

The current shortcuts add two keyboard shortcuts to the notebook editor:
 * Ctrl Shift ArrowUp: move cell up
 * Ctrl Shift ArrowDown: move cell down

You must not be editing the cell. The cell to move must be selected just to the
left and is denoted by a vertical bar highlighting the cell.
