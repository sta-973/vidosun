@echo off
echo ================================
echo   UPDATE VIDOSUN WEB GITHUB
echo ================================
git add .
git commit -m "update otomatis"
git push origin master
echo -------------------------------
echo   ✅ Update berhasil dikirim ke GitHub!
echo   Tunggu beberapa detik agar hosting Render/niagahoster menarik update.
echo -------------------------------
pause
