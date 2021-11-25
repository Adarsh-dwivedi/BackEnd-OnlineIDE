import uuid
import os
import subprocess
import django
django.setup()

def create_file(code, language):
    extension = {
        "cpp": "cpp",
        "python": "py",
        "c": "c"
    }
    file_name = f"{str(uuid.uuid4())}.{extension[language]}"
    with open(os.path.join("code", file_name), 'w') as f:
        f.write(code)

    return file_name

def execute_file(file_name, language, submission):
    if(language=="cpp"):
        compile_output = subprocess.run(["g++", os.path.join("code", file_name)], stdout=subprocess.PIPE, text=True)
        if(compile_output.returncode!=0):
            #compile time error
            submission.status = "E"
            submission.save()
            return

        run_output = subprocess.run(["a.exe"], stdout=subprocess.PIPE, text=True)

        if(run_output.returncode!=0):
            #runtime error
            submission.status = "E"
            submission.save()
            return


        submission.output = run_output.stdout
        submission.status = "S"
        submission.save()
