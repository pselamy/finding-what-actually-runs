Source map from the install script and application source:
- `service/server.py` starts the HTTP service and passes PATCH requests to the installed handler.
- `service/registration.py` selects an installed handler using the workspace settings. The handlers are in `service/desk.py` and `service/team.py`.
- Each handler calls its own `*_normalize.py` and `*_persist.py` helpers. Which sequence it uses depends on the snapshot layout.
- The CLI loads the supplied snapshot at startup. The source map describes the possible routes in the repository.
