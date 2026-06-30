@echo off
echo ========================================================
echo          REDROB CANDIDATE RANKING SYSTEM
echo ========================================================
echo.

echo [1/3] Generating synthetic candidate dataset...
python candidate_generator.py
if %ERRORLEVEL% neq 0 (
    echo Error running candidate_generator.py. Please verify Python is installed and in your PATH.
    pause
    exit /b %ERRORLEVEL%
)
echo Success: Dataset generated.
echo.

echo [2/3] Executing candidate ranking engine...
python ranking_engine.py
if %ERRORLEVEL% neq 0 (
    echo Error running ranking_engine.py.
    pause
    exit /b %ERRORLEVEL%
)
echo Success: Rankings compiled and saved to submission.csv.
echo.

echo [3/3] Launching Streamlit web dashboard...
echo Launching Streamlit in browser...
streamlit run app.py
if %ERRORLEVEL% neq 0 (
    echo Error starting Streamlit app. Please ensure streamlit is installed (pip install streamlit pandas).
    pause
    exit /b %ERRORLEVEL%
)

pause
