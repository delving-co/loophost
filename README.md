# Loophost

## Localhost management for the 21st century

Install with pip.
Run as sudo (so we can bind to 80 and 443 and then setuid down.)
Visit localhost in a browser for configuration.

## For testing webssocket:
```curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: poet.joshuamckenty.loophost.dev" -H "Origin: https://poet.joshuamckenty.loophost.dev" https://poet.joshuamckenty.loophost.dev/status```