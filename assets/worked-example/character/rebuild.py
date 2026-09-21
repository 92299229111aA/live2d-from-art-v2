"""Rebuild original-pixel parts, eye and mouth rigs, and portable/web runtime."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['extract_reference.py','prepare_eyes.py','prepare_mouth.py','prepare_expression_hair.py','build_moc.py','validate_native.py']:
 subprocess.run([sys.executable,str(root/script)],cwd=root,check=True)
