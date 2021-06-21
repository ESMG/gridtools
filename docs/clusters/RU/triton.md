# Rutgers Triton cluster

This is information for using the RU:triton cluster.

This information is based on using a ssh key to alnilam.

# Start an interactive node

```
srun --nodes=1 --ntasks-per-node=1 --time=01:00:00 --pty bash -i
```

Ensure the environment is ready to run gridtools.

Find the IP address of the interactive node and start jupyter lab.

```
jupyter lab --ip=192.168.1.30 --no-browser
```

Copy the link with http://127.0.0.1 for use later.

# Forward ports

From your local machine forward port 8888.  Add port 8787 if also
using dask.

```
ssh -A -X -Y -L 8888:localhost:8888 -L 8787:localhost:8787 cermak@alnilam.esm.rutgers.edu
```

Once connected to alnilam, forward ports to triton and the
interactive node running jupyter lab.

```
ssh -A -X -Y -L 8888:192.168.1.30:8888 -L 8787:192.168.1.30:8787 triton
```

Once the ssh forwarding is setup, in a browser on your local machine use
the http://127.0.0.1 link copied from above.
