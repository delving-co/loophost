# Loophost aka fling.dev

## Localhost management for the 21st century

Install with pip.
Run as sudo (so we can bind to 80 and 443 and then setuid down.)
Visit localhost in a browser for configuration.

## For testing webssocket:
```curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: poet.joshuamckenty.fling.dev" -H "Origin: https://poet.joshuamckenty.fling.dev" https://poet.joshuamckenty.fling.dev/status```