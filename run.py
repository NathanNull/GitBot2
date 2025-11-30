from multiprocessing import Pool
from subprocess import Popen, PIPE, STDOUT
from sys import platform

# requires that you have a venv set up, so
# the script knows where to run python files from
bot = [".venv/Scripts/python.exe"\
    if platform not in ["linux", "linux2"]\
    else "python", "bot/main.py"]
website = "flask --app=website/website run" if platform not in ["linux", "linux2"] else "sudo ~/SurfBot/.venv/bin/flask --app=website/website.py run -h 0.0.0.0 -p 80"

def run_file(input_):
    cmd, prefix = input_
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    print(f"{prefix:>7}Started.")
    while True:
        # Get line
        try: line = proc.stdout.readline()

        # Check end cases
        except KeyboardInterrupt: break
        if not line: break
        if proc.returncode is not None: break

        # Log stdout with prefix
        print(f"{prefix:>7}{line.decode('UTF-8')}", end="")

def main():
    proc_names = [
        (bot, "BOT: "),
        (website, "FRONT: "),
    ]
    try:
        with Pool(len(proc_names)) as pool:
            pool.map(run_file, proc_names)
    except KeyboardInterrupt:
        print("Done!")

if __name__ == "__main__":
    main()