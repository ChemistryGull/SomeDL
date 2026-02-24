# General python installation on windows:
- Download the installer from the website
- Say yes to everything in the installer
- Install somedl via py -m pip install somedl

### If somedl command is not recognized, add the python scripts folder to path (This is not a somedl problem, this is a general python setup issue):
- The path is typically something like `C:\Users\YourName\AppData\Local\Programs\Python\pythoncore-3.14-64\Scripts` depending on your python version and mode of installation
- Type "environment variables" in the search, open "Edit the system environment variables"

![6_search_environment](images/ffmpeg/6_search_environment.png)

- In there, at the bottom click "Environment Variables..."

![7_env_var](images/ffmpeg/7_env_var.png)

- Click on "Path" and then "Edit"

![8_edit_path](images/ffmpeg/8_edit_path.png)

- Click "New" and then paste the path of your scripts folder in there. It should look similar to this:

![correct_python_vars](images/ffmpeg/correct_python_vars.png)

- Click OK on all windows
- Reopen all CMD or PowerShell windows
