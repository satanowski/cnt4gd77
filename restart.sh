# Send HUP signal to master gunicorn process
sudo kill -HUP `ps -aef | grep gunicorn | grep gd77 | awk '{print $2}' | sort | head -1`