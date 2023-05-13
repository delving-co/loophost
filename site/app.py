from fling.start import app, start_app


domain_name = "fling.dev"


def main():
    return """
<pre>Welcome to loophost.

WHAT: Turnkey localhost management for students, freelancers, agencies and development teams of all sizes.

WHY: Because it's 2023, and friends don't let friends run without SSL.

HOW: Log in with fling auth (using your GitHub credentials), and we'll do the rest.
Specifically, we'll generate a private key (that never leaves your computer) and set up
DNS records and SSL certificates for *.&lt;github-username&gt;.fling.dev.

When you visit https://yourapp.username.fling.dev, you'll be able to choose any locally
running web app (in any language, and on any port or web socket) to bind to that name.

BONUS: Ready to share your work with others? Simply flip the "sharing" toggle on
https://username.fling.dev for that app, and we'll TUNNEL traffic from the public internet
to your local machine, from https://yourapp.username.fling.wtf.

DOUBLE BONUS: Not ready to share with EVERYONE in the world? Enable "secured" sharing,
and you can issue individual certificates to each of your collaborators. (No password required).
No cert? No peeking.

WHAT ABOUT...
Websockets? Yep.
Mobile app development? Of course.
Running in debug mode? Absolutely. Breakpoints work just as you would expect.
How many apps can I have running? We have no idea, let's find out together.

</pre>"""


start_app(main, domain_name=domain_name)