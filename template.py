import os

list_of_files = [

    'setup.py',
    'requirements.txt',
    'README.md',
    'LICENSE',
    'MANIFEST.in',
    'Makefile',
    'Dockerfile',
    '.dockerignore',
    '.gitignore',
    '.gitattributes',
    '.editorconfig',
    '.bumpversion.cfg',
    'research/research.ipynb',
    'docker-compose.yml',
    'app.py',
    'src/__init__.py',
    'src/constant/__init__.py',
    'src/utils.py/__init__.py',
    'src/utils.py/common.py',
    'src/models.py',
    'src/prompts/__init__.py',
    'src/prompts/prompts.py',
    'models/config.yml',
    'database/config.yml',
    'src/exception/__init__.py',
    'src/logger/__init__.py',
    'src/pipeline/__init__.py',
    'src/pipeline/flow_pipeline.py',
    'src/components/__init__.py',
    'src/entity/__init__.py',
    'src/entity/entity.py',
]


def create_files():
    for file in list_of_files:
        directory = os.path.dirname(file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write('')
            print(f'Created {file}')
        else:
            print(f'{file} already exists')


def main():
    create_files()

if __name__ == '__main__':
    main()
