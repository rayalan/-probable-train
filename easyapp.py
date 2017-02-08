#!/usr/bin/env python
from tutorial.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', debug=True)  # Use this line for vagrant to access from host machine.
