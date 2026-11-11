"""Load a local KEY=VALUE file and run Python without putting keys in arguments."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env', default='.env', help='Local configuration path')
    parser.add_argument('python_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.python_args
    if command[:1] == ['--']:
        command = command[1:]
    if not command:
        parser.error('Provide a Python script or -- -m module.')
    root = Path(__file__).resolve().parent
    try:
        values = {}
        for line in (root / args.env).read_text(encoding='utf-8-sig').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            name, separator, value = line.partition('=')
            name, value = name.strip(), value.strip()
            if not separator or not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
                raise ValueError('Invalid configuration format.')
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[name] = value
        env = {**os.environ, **values, 'PYTHONIOENCODING': 'utf-8'}
        if env.get('OPENAI_BASE_URL', '').rstrip('/') == 'https://api.deepseek.com' and 'DEEPSEEK_API_KEY' in values:
            env['OPENAI_API_KEY'] = values['DEEPSEEK_API_KEY']
    except (OSError, ValueError):
        print('Cannot load local configuration. Check the path and KEY=VALUE format; values are not displayed.', file=sys.stderr)
        return 2
    return subprocess.run([sys.executable, *command], cwd=root, env=env).returncode


if __name__ == '__main__':
    sys.exit(main())
