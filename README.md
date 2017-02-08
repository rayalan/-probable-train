
Setup
=====

Vagrant
-------

First, install vagrant + virtual box according to the vagrant instructions. Then...

    vagrant up

Now, launch Redis, once for test port and once for production.

    vagrant ssh  # Console 1, production
    sudo redis-3.2.7/src/redis-server --port 6380

    vagrant ssh  # Console 2, test
    sudo redis-3.2.7/src/redis-server --port 6379

Edit easyapp.py to use line 8 instead of line 7, since we're using vagrant and need a web server that allows any outside host to connect; we'll depend on our host firewall to keep us safe.

And launch the web server...

    vagrant ssh  # Console 3
    cd /tutorial
    virtualenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    ./easyapp.py

And run the tests...

    vagrant ssh  # Console 4
    cd /tutorial
    python -m tutorial.test.tutorialtest

Desktop
-------

If you have redis installed/built along with Python2 with pip and virtualenv installed, you can use the commands above, dropping the vagrant sections and running the rest from the project root.

Redis doesn't need to be run as root; it's only that way here because of how vagrant provisions.

Demo
====

Get a list of routes

    curl 127.0.0.1:5000/routes.doc
    curl 127.0.0.1:5000/routes.json

Fail to login

    curl bob:@127.0.0.1:5000/auth/login

Get a login cookie

    curl -v alan.ray:bob@127.0.0.1:5000/auth/login

Find out how much the game is worth, then place a bet

    curl 127.0.0.1:5000/game/wager/amount
    curl 127.0.0.1:5000/game/wager/amount/50

Place a bet with for me

    curl --cookie="session=[cookie we got up above]" 127.0.0.1:5000/game/wager/amount/50

And let's rig the winner of the game

    127.0.0.1:5000/game/outcome/alan -X POST

Ah, only special people can rig the game.

    curl --cookie="session=[cookie we got up above]" 127.0.0.1:5000/game/outcome/alan -X POST

And let's end the game and see who won

    curl 127.0.0.1:5000/game/state/resolve -X POST
