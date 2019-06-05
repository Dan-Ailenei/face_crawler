import os
import sys


if __name__ == '__main__':
    req_path = os.path.join('..', '..', 'requirements.txt')
    os.system(f"pip install -r {req_path}")
    os.system("pip install cmake")
    os.system("pip install face_recognition")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line([sys.argv[0], "makemigrations", "models"])
    execute_from_command_line([sys.argv[0], "migrate"])

    print("If you want to make available the run_crawler command from anywhere, you should add this path to the env path\n"
          "If you are on linux you could use a sheebang and if you are on windows you can associate the .py extention "
          "with a certain command. For that you could run the next commands with administrator rights. \n"
          "assoc .py=Python\n"
          '"ftype Python="PATH_TO_PYTHON_INTERPRETER.exe" "%1" %*"')
