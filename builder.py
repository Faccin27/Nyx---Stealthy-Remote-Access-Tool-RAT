import os
import shutil
import subprocess
import zipfile
import requests

class Build:

    def __init__(self) -> None:
        self.build_dir = os.path.join(os.getcwd(), 'build')
        self.dist_dir = os.path.join(os.getcwd(), 'dist')
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.dist_dir, exist_ok=True)

    def get_upx(self) -> None:

        url = 'https://github.com/upx/upx/releases/download/v3.96/upx-3.96-win64.zip'
        zip_path = os.path.join(self.build_dir, 'upx.zip')

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.build_dir)

    def build(self) -> None:
        pyinstaller_executable = shutil.which('pyinstaller')
        if pyinstaller_executable is None:
            raise RuntimeError("Pyinstaller is not installed or not in path")
        
        main_file =  os.path.join(os.getcwd(), 'main.py')
        plugins_dir = os.path.join(os.getcwd(), 'plugins')

        subprocess.run([
            pyinstaller_executable,
            '--onefile',
            '--noconsole',
            '--clean',
            '--distpath', self.dist_dir,
            '--workpath', os.path.join(self.build_dir, 'work'),
            '--specpath', os.path.join(self.build_dir, 'spec'),
            '--upx-dir', os.path.join(self.build_dir, 'upx-3.96-win64'),
            '--add-data', f'{plugins_dir};plugins',
            main_file
        ], check=True)

if __name__ == "__main__":
    builder = Build()
    builder.get_upx()
    builder.build()