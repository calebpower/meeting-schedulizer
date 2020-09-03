# Meeting Schedulizer

_Meeting your goals, when meetings are your goal._
 
This application was originally designed as a submission for the UCO Fall 2020 Computer Science capstone course.

## Original Contributors

| Name            | Responsibilities                                  |
|:----------------|:--------------------------------------------------|
| Hampton, Justin | Software Engineer                                 |
| Le, Brian       | Software Engineer                                 |
| Power, Caleb    | Software Engineer, Git Administrator              |
| Sakurai, Yosuke | Software Engineer                                 |
| Sim, Minbo      | Software Engineer                                 |
| Tull, Courtney  | Software Engineer, Lead Quality Assurance Analyst |
| Waldrip, Jacob  | Software Engineer, Product Owner, Scrum Master    |

## Installation

To build and install the project from source, we recommend doing the following:

1. Install [Python 3](https://www.python.org/)
2. Install [pip](https://pypi.org/project/pip/)
3. Install [virtualenv](https://virtualenv.pypa.io/en/stable/installation.html)
4. Create a new virtual environment by executing `mkvirtualenv meeting-schedulizer`
5. If the virtual environment isn't already active, do `workon meeting-schedulizer` (you can leave at any time with `deactivate`)
6. Run `python manage.py runserver`
7. If you have any messages that indicate that you should perform a migration, leave by hitting `CTRL + C` and then do `python manage.py migrate`, and then do step 6 again.
8. Visit your browser at `http://127.0.0.1:8000`

You can learn more by reading about [Pipenv & Virtual Environments](https://docs.python-guide.org/dev/virtualenvs/).

If at any point during this process you have trouble with `pip` or `python` not being recognized commands, ensure that you've added them to your `$PATH` variable. (Or, if you're on Windows, the `%PATH%` variable.)
