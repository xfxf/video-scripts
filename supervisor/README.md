Video Scripts deployment with Supervisor
----------------------------------------

Note that supervisor 3.2 was used here, and ubuntu only currently offers 3.0. This may
be important for environment variable substitution used in the configuration file as this
only partially works in 3.0.

Python 2 (the default /usr/bin/python on Ubuntu 15.10) is used, NOT python 3.

Rather than installing via apt-get, use pip to install:

    $ sudo apt-get install python-pip   (does not seem to be installed by default!)
    $ sudo pip install supervisor

or, use the git repo and check out v3.2 (python 3 porting is in process, and there are
a few open issues on this post 3.2 that may affect running it on python 2.x, so we
avoid it rather than using HEAD).

    $ git clone https://github.com/Supervisor/supervisor
    $ cd supervisor
    $ git checkout 3.2.0
    $ sudo pip install .

(using a virtualenv is for various reasons better practice, however this is left as
an exercise for the reader).

* Use the run_supervisor script in bin/ for starting supervisord as the videoteam user.
* Use the run_supervisorctl script for the controler interface. adding -i provides an interactive shell.
* Point a web browser at http://localhost:9001/ for the web interface

For remote use, apt-get install nginx and add the following to its configuration:

    upstream supervisor { 
      server 127.0.0.1:9001 fail_timeout=0; 
    }

    server {

      # server configuration

      location /supervisor {
        return 301 $uri/index.html;
      }

      location /supervisor/ {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # hack the host https://github.com/Supervisor/supervisor/issues/251
        proxy_set_header Host $http_host/supervisor/index.html;
        proxy_redirect off;
        rewrite ^/supervisor(.*)$ /$1 break;
        proxy_pass http://supervisor;
      }
    }

which will make it directly available at http://yourhostname/supervisor/. Do NOT run nginx under supervisord control, but install and run locally as usual:

    $ sudo apt-get install nginx

should be enough to get it up and running, returning a bland example page at http://yourhostname/, and supervisor control at /supervisor/ once the above is added to nginx configuration and nginx restarted.

Note that there are a few cluster management solutions available for supervisor (mentioned in the supervisor docs):

1. cesi  - (https://github.com/Gamegos/cesi) python/flask framework, probably best choice
3. suponoff  - (https://github.com/GambitResearch/suponoff) django (1.7) app foss-compatible license
2. django-dashadvisor  - (https://github.com/aleszoulek/django-dashvisor) django app, no license in repository, ancient version of django
4. other nodejs and php based options are also available (listed in the supervisor docs)

