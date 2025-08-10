import os


print_cwd = os.getcwd()

path = "/recordings/test.wav "
path2= "main.py"
check_files = os.path.isfile(os.getcwd(path))

print(print_cwd)
print(check_files)
