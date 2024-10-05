@echo off
python -m venv testenv

call testenv\Scripts\activate.bat

pip install -r requirements.txt

echo 虛擬環境已創建並激活。要退出虛擬環境，請運行 deactivate 命令。
