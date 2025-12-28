# Dynamic-Shelf-Space-Allocation-Program
National Yang Ming Chiao Tung University - Supply Chain Management Lab 005
Project files: https://drive.google.com/drive/folders/1d-MYQO56dG-KJ1oyyRLvfyPM6vdJG03s?usp=drive_link

## 專案開發流程:

為了保持 `main` 分支的穩定，請務必遵守以下「功能分支」開發流程：
### 1. 同步最新進度 (Start)
每次開工前，請先更新本地端的主分支：
```
git checkout main
git pull origin main
```
### 2. 建立功能分支 (Branch)
不要直接修改main，請建立分支，規範如下:
命名範例：feature/你的名稱or代號-分支功能
```
git checkout -b feature/suuu-RAG功能開發
```
### 3. 提交變更 (Commit)
完成一個段落後進行存檔：
提交規範："[修改類型]: 詳細描述修改內容"
```
git add .
git commit -m "清楚描述修改內容"
```
### 4. 推送到遠端 (Push)
將分支上傳至伺服器：
```
git push
or
git push --set-upstream origin feature/你的功能名稱
```
### 5. 發起合併請求 (Pull Request)
前往GitHub網頁。
點擊 "New Pull Request"。
指定 Reviewer 審核，通過後進行 Merge。
