from pathlib import Path

hook_path = Path(__file__)
raise RuntimeError

datas = [
    (hook_path.parent.parent / 'img', './img/')
]

binaries = []
