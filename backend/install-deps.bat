@echo off
echo 正在安装后端依赖...

REM 检查是否已存在虚拟环境
if exist .venv (
    echo 检测到现有的虚拟环境，正在激活...
    call .venv\Scripts\activate
) else (
    echo 创建新的虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo 错误：无法创建虚拟环境，请确保已安装Python
        pause
        exit /b 1
    )
    call .venv\Scripts\activate
)

echo 正在升级pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo 错误：无法升级pip
    pause
    exit /b 1
)

echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误：无法安装依赖，请检查错误信息
    pause
    exit /b 1
)

echo 依赖安装完成！
pause