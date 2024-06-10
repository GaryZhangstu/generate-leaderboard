import os
import subprocess
import sys

def get_package_size(package_name):
    result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if line.startswith('Location:'):
            location = line.split('Location: ')[1]
            package_path = os.path.join(location, package_name.replace('-', '_'))
            if os.path.exists(package_path):
                return sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, _, filenames in os.walk(package_path)
                           for filename in filenames)
    return 0

def main():
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
    lines = result.stdout.split('\n')[2:]  # skip header lines
    packages = [line.split()[0] for line in lines if line]

    total_size = 0
    for package in packages:
        size = get_package_size(package)
        total_size += size
        print(f'{package}: {size / (1024 ** 2):.2f} MB')

    print(f'Total size: {total_size / (1024 ** 2):.2f} MB')

if __name__ == '__main__':
    main()
