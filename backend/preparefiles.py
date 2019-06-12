# python wrapping for prepearing file system script
import subprocess  # safelly run bash scripts from python
import sys  # redirect stdout


def deploy(user_id, arch, path):
    # run bash script and redirect stdout
    sub = subprocess.run(["./backend/preparefiles.sh", str(user_id), arch, path],
                         stdout=sys.stdout)
    if not sub.returncode:
        print("ok")
        return(0)
    else:
        return(sub.stderr)
        return(1)


def main():
    pass


if __name__ == '__main__':
    main()
