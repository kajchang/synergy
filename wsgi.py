from app import app as application

import os

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=os.environ.get('PORT'))
