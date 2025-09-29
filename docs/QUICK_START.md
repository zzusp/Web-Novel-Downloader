# 快速开始指南

## 🚀 立即开始

### 方式1: 使用Python构建脚本（推荐）

```bash
# 查看所有可用命令
python scripts/build/build.py --help

# 构建Python包
python scripts/build/build.py --packages

# 构建Windows可执行文件
python scripts/build/build.py --exe windows

# 构建所有内容
python scripts/build/build.py --all
```

### 方式2: 手动构建

```bash
# 构建Python包
python -m build

# 构建Windows可执行文件
pyinstaller book_downloader.spec --clean
```

## 📦 安装和使用

### 安装Python包
```bash
pip install dist/book_downloader-1.0.0-py3-none-any.whl
book-downloader --help
```

### 使用可执行文件
```bash
# Windows
dist\book-downloader.exe --help
dist\book-downloader.exe parse <URL>
dist\book-downloader.exe download <book_id>
```

## 🛠️ 开发环境设置

### 安装开发依赖
```bash
pip install -e ".[dev]"
```

### 运行测试
```bash
# 使用Python命令
python -m pytest tests/ -v

# 或使用构建脚本
python scripts/build/build.py --test
```

### 代码格式化
```bash
python -m black src/ scripts/ tests/
```

### 代码检查
```bash
python -m flake8 src/ scripts/ tests/
python -m mypy src/ scripts/
```

## 📚 更多信息

- **详细使用说明**: [USAGE_GUIDE.md](USAGE_GUIDE.md)
- **项目结构说明**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **开发日志**: [spec/develop-logs/](spec/develop-logs/)

## ❓ 常见问题

### Q: 如何构建macOS可执行文件？
A: 需要在macOS系统上运行：`python scripts/build/build.py --exe macos`

### Q: 构建失败怎么办？
A: 检查依赖是否安装完整：`pip install -r requirements.txt` 和 `pip install pyinstaller`

### Q: 如何运行测试？
A: 使用 `python -m pytest tests/ -v` 或 `python scripts/build/build.py --test`
