# EFTYTLiveTool
因爲打開瀏覽器做Youtube直播，每次都要設定資料太麻煩

所以寫了這個東西出來

---

# 依賴
```
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
pytz
pyinstaller
```
> pyinstaller 是用來打包成exe的，如果不需要可以忽略
>
> 之前也嘗試過用request, 但 Google 好像限制了用 request 的操作可以做到的事情

# 使用方法:
## 下載項目
```bash
git clone https://github.com/SvCpu/EFTYTLiveTool.git
```
> 如果你不會git, 可以直接下載項目的zip並解壓縮

## 安裝虛擬環境
請確保你已經安裝 Python3 環境(我用的是3.11.9)

### Windows

運行`setup_venv.ps1`或`setup_venv.bat`腳本

### Linux
```bash
sudo apt-get install python3-venv
```
運行`setup_venv.sh`腳本

## 執行腳本
### Windows
雙擊`run_script.cmd`腳本即可

### Linux
```bash
./run_script.sh
```
## 獲取`client_secret.json`
1. 在[Google Console](https://console.cloud.google.com/)申請一個項目
2. 打開`API 和服務`
![image](/img/GoogleConsoleHome.png)
3. 點選左上角的`啓用 API 和服務`，然後搜索`YouTube Data API v3`
![image](/img/GoogleConsoleApiPage.png)
4. 點選`啓用`
![image](/img/啓用api.png)
5. 點選左邊的`憑證`
![image](/img/憑證.png)
6. 點選左上角的`建立憑證`，選擇`OAuth用戶端ID`
![image](/img/OAuth用戶端ID.png)
7. 點選左邊的`設定同意畫面`
![image](/img/設定同意畫面.png)
以下是我的選擇，請你根據自己的需求選擇選項
```
User Type:外部
```
8. 設置完成後前往`OAuth 同意畫面`, 點選`發布應用程式`
![image](/img/發佈狀態.png)
看到`實際運作中`則表示成功
9. 點選左邊的`憑證`
![image](/img/憑證.png)
10. 點選左上角的`建立憑證`，選擇`OAuth用戶端ID`
![image](/img/OAuth用戶端ID.png)
```
應用程式類型: 網頁應用程式
```
11. 完成操作後，在出現彈窗中點選`下載 JSON`
![image](/img/OAuth用戶端已建立.png)
12.  將下載的`client_secret.json`放在項目的目錄
> - 記得重命名爲`client_secret.json`
>
> - 第一次執行的時候，可能會彈出一個瀏覽器界面，要求你驗證
>
> - 記得去憑證那裏把`已授權的重新導向 URI`, 改成程序裏面的地址(main.py的`redirect_uri`)

# 免責聲明
本人並非專業的程序員, 所以可能會有一些bug, 使用前請確定您能承受使用這個項目可能導致的問題, 

如果發現問題或者有什麼意見請提出issue

這個項目與 YouTube 官方無關, 只是我自己用來開啓直播的一個小工具

# 授權條款
本項目採用 [Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0) 授權條款。
