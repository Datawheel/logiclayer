# Feature draft

* Log all requests using `app.logger` on their applicable levels  
  This is an instance of python's logging.Logger class, so check documentation on how to implement custom targets:
   * https://www.datadoghq.com/blog/python-logging-best-practices/
   * https://flask.palletsprojects.com/en/1.1.x/quickstart/#logging

* Implement a JWT middleware to authenticate and control permissions
  This would probably require tweaking the routes themselves
  The olap-proxy module would also have to pass the header
