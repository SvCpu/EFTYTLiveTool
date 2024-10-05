# 創建虛擬環境
python -m venv testenv

# 激活虛擬環境
.\testenv\Scripts\Activate.ps1

# 安裝 requirements.txt 中的依賴
pip install -r requirements.txt

Write-Host "虛擬環境已創建並激活。要退出虛擬環境，請運行 'deactivate' 命令。"
