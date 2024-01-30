pyinstaller --noconfirm --log-level=WARN ^
    --onefile ^
    --hidden-import pyparsing ^git 
    --name "rbr_setup_compare" ^
    rbr_setup_compare.py