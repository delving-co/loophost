# Loophost : Local web hosting for the 21st century

## What is Loophost?

Similar to nginx or apache, Loophost allows you to use your laptop or desktop as a server.
Designed for REALLY BUSY PEOPLE, it makes it really fast and easy to:

 * Get a unique domain name for every local app you're working on
 * Get a REAL WORLD SSL CERTIFICATE for each of those (for free)
 * Connect to those apps over local network ports (like the 'localhost:5000' thing you've been doing)
 * Connect over unix domain sockets (usually 2-3 TIMES FASTER than local network ports)

This addresses a whole bunch of small, annoying everyday problems for developers:

 * You can build and test remote content (including from APIs and other components) without "mixed content" problems.
 * You can run multiple apps (frontend and backend, or different microservices) without trying to remember which one is on what port
 * You can use and test CORS headers properly
 * You can use and test OAuth workflows and callbacks without weird special cases for the non-SSL localhost
 * You won't accidentally mix and break cookie domains because localhost and 127.0.0.1 aren't really the same thing

And then it gets better: with a single click in a web interface (or an HTTP post, if you'd rather), you can enable a reverse tunnel for _that app only_, and share that with anyone.

 * The mobile or IoT app you're developing can run on the iPhone, android, iPad, 
    Raspberry Pi or Arduino you've got in your house, and still talk to the API 
    on your desktop
 * Working in the office with a bigger team? They can use the live version of the
 frontend you're working on, talking to the live version of the backend they're working on
  - all without any commit-build-deploy loop in the way, or the cost and latency of 
  shared dev servers somewhere else.

We don't have time to write yaml. And we definitely don't have time to restart servers. 
Every modern web framework will *watch* our source files, and rebuild and restart when needed - 
so loophost works that way, too. This means that you can use STATEFUL connections like Websockets
and SSE, without having those connections torn down because a completely DIFFERENT app needed 
an updated configuration.

## Installation

Install with pip: `python3 -m pip install loophost`

Then run `python3 -m loophost.postinstall`

This will open a browser window to authenticate with your GitHub account. 
Then, it will prompt you for your password.
Finally, it will open a browser window to your local LoopHost admin screen.

![Screenshot of Loophost admin screen](https://loophost.dev/static/loophost-screenshot.png)

## Uninstalling

If you're done with loophost, simply run `python3 -m loophost.uninstall`. You will
once again be prompted for your password (to remove the server components). Then
you can use `pip3 uninstall loophost` to remove the last of it.

Note that the `~/.flingdev` folder will remain with a `flinguser.txt` file in it.
If you aren't using any other `fling` components and services, you can safely
delete it.

## Security Questions

### Why do you need me to log into GitHub?

We need to guarantee that each Loophost user is unique to avoid collisions.
We also need to make sure that they can't hijack each other's domain names.
Rather than build and maintain a new identity system, we use a GitHub app.
Your github username IS your loophost username.

The current token for your GH session is stored in your local keychain,
(never unencrypted) and is passed through HTTP headers to all the server-side API calls. 

### Why does the install prompt me for my password?

In order to listen on the default web ports of 80 and 443, the `loopproxy`
component of loophost has to be run as the root user. All the other
components of loophost (including the local web interface and the ssh tunnels)
will run as launchd agents of the installing user.


## Technical Details

Loophost has five main components:

 * The loopproxy
 * The admin web interface
 * Dynamic ssh tunnels
 * The USER and DNS API server
 * The tunneling server

### Loopproxy

Loophost originally used uwsgi for a reverse proxy server. However, uwsgi is unmaintained,
and sadly some of the most exciting features (such as embedded web apps) only work on Linux.
Inspired by [a blog post by Fideloper](https://fideloper.com/go-http), we decided to write
a Golang-based reverse proxy that is dynamically configured through a single JSON file.

(In the near future, this should allow us to cross-compile for Windows and Linux as well as Mac OS X - as soon as we have a chance to learn how to run daemons on Windows.)

### The admin web interface

The admin interface uses [fling-start](https://github.com/10in30/fling-start), which is a small wrapper around [Flask](https://flask.palletsprojects.com/en/2.3.x/) for building
python web apps *Really Fast(tm)*. It makes it easy to edit the JSON file that drives loopproxy.
It also makes API calls to set up tunneling credentials, and system calls to register and unregister
the SSH agents for those tunnels.

### Dynamic SSH tunnels

When an app is "shared", we create a local [launchd](x-man-page://launchd) agent that runs ssh to perform the port forwarding.
These agents are defined by XML in the plist format, which is saved into ~/Library/LaunchAgents.
The launchd service takes care of restarting these agents.

### The USER and DNS server

The API that supports ACME verification via DNS-01 challenges, manages the GitHub login flow, and
pushes public keys into the tunneling server is part of the [fling`](https://github.com/10in30/fling/tree/main/fling-api) project. It provides an OpenAPI interface which is 
running at https://api.fling.wtf/docs; we access this through [an autogenerated client](https://github.com/10in30/fling/tree/main/fling-client).

### The Tunneling server

We use the amazing [sish](https://github.com/antoniomika/sish) software for the tunneling endpoint. A rough approximation of the config we use is in `tunnels/config.sh`.


## Troubleshooting / Known Issues

If you uninstall and re-install more than 5 times in 165 hours, the Letsencrypt servers will
rate-limit certificate issuance. To avoid this, you can re-run the postinstall script _without_
running the uninstall scripts in between. (Uninstall deletes all the certificates and keys, 
whereas during reinstall they are not renewed because they _probably_ haven't expired).

If your local certificates expire, you can rerun the postinstall script and they will 
probably(?) be renewed.

As each ssh tunnel is enabled, a toaster popup will appear on your Mac desktop. Changing
launchd settings from this UI is unsupported (and we have no idea what will happen.)

The plist files contain the full path to the version of python that was running when loophost
was installed. If you upgrade python, loophost will probably keep working with the old version -
but we haven't tested python upgrades yet.

Access to the GitHub token stored in `keychain` is limited to certain files and scripts. If
attempts to enable tunneling fail, it's possible that this is the problem. You can try opening
Keychain Access and searching for the two saved passwords named `fling-github-token`. Setting
the Access Control to "allow all applications to access this item" may help.

## Contributing

As you can probably see, this project isn't "contribution ready" quite yet. If you still 
want to dive in and help out, please drop us a note or an email before you start building
so that we can make sure we're well aligned.