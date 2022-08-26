from multiprocessing import Pool
from subprocess import Popen, PIPE, STDOUT

python = ".venv/Scripts/python.exe"

def run_file(input_):
    path, prefix = input_
    proc = Popen(f"{python} {path}", stdout=PIPE, stderr=STDOUT)
    while True:
        # Get line
        try: line = proc.stdout.readline()

        # Check end cases:
        except KeyboardInterrupt: break
        if not line: break
        if proc.returncode is not None: break

        # Log stdout with prefix
        print(prefix+line.decode("UTF-8"), end="")

def main():
    proc_names = [
        ("website/w_backend.py", "backend says "),
        ("website/website.py", "frontend says "),
        ("bot/main.py", "bot says ")
    ]
    try:
        with Pool(len(proc_names)) as pool:
            pool.map(run_file, proc_names)
    except KeyboardInterrupt:
        print("Done!")

if __name__ == "__main__":
    main()