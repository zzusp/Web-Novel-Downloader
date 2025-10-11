# 项目结构说明

## 📁 标准Python项目结构

```
Web-Novel-Downloader/
├── src/                           # 源代码目录
│   └── book_downloader/           # 主包
│       ├── __init__.py
│       ├── cli.py                 # 命令行接口
│       ├── core.py                # 核心逻辑
│       ├── epub_generator.py      # EPUB生成
│       ├── metadata.py            # 元数据管理
│       ├── utils.py               # 工具函数
│       ├── config.py              # 配置管理
│       ├── config_manager.py      # 配置管理器
│       ├── config_validator.py    # 配置验证器
│       └── task_executor.py       # 任务执行器
├── scripts/                       # 脚本目录
│   ├── __init__.py
│   ├── book_downloader.py         # 主入口脚本
│   └── build/                     # 构建脚本
│       └── build.py               # Python构建脚本
├── tests/                         # 测试目录
│   ├── __init__.py
│   ├── conftest.py                # pytest配置
│   ├── test_config.py
│   └── test_utils.py
├── configs/                       # 配置文件目录
│   └── example.json               # 示例配置文件
├── spec/                          # 规范文档
│   ├── development-progress.md    # 开发进度
│   └── develop-logs/              # 开发日志
│       ├── 2025-09-02-*.md
│       ├── 2025-09-27-*.md
│       └── 2025-09-29-*.md
├── dist/                          # 构建输出目录
│   ├── web-novel-downloader.exe   # Windows可执行文件
│   ├── web_novel_downloader-1.0.0-py3-none-any.whl
│   └── web_novel_downloader-1.0.0.tar.gz
├── build/                         # 临时构建目录（自动生成）
├── *.egg-info/                    # 包信息目录（自动生成）
├── pyproject.toml                 # 现代Python项目配置
├── setup.py                       # 传统Python包配置
├── requirements.txt               # 依赖列表
├── MANIFEST.in                    # 包含文件清单
├── build_win.spec                # PyInstaller Windows配置
├── build_macos.spec              # PyInstaller macOS配置
├── README.md                      # 项目说明
├── USAGE_GUIDE.md                 # 使用指南
├── QUICK_START.md                 # 快速开始指南
├── PROJECT_STRUCTURE.md           # 项目结构说明（本文件）
├── LICENSE                        # 许可证
└── .gitignore                     # Git忽略文件
```

## 🛠️ 构建系统

### 标准构建方式

1. **Python包构建**
   - 使用 `python -m build`（现代方式）
   - 使用 `python setup.py sdist bdist_wheel`（传统方式）

2. **可执行文件构建**
   - 使用 `pyinstaller` 命令行工具
   - 通过 `.spec` 文件配置

3. **构建自动化**
   - `scripts/build/build.py` - Python构建脚本

### 构建命令

```bash
# 使用Python构建脚本（推荐）
python scripts/build/build.py --help

# 开发安装
pip install -e ".[dev]"

# 构建Python包
python scripts/build/build.py --packages
# 或手动构建
python -m build

# 构建可执行文件
python scripts/build/build.py --exe windows    # Windows
python scripts/build/build.py --exe macos      # macOS
# 或手动构建
pyinstaller build_win.spec --clean

# 构建所有内容
python scripts/build/build.py --all

# 清理构建文件
rm -rf build/ dist/ *.egg-info/
```

## 📦 分发格式

### Python包
- **Wheel包** (`.whl`) - 二进制分发，推荐使用
- **源码包** (`.tar.gz`) - 源码分发

### 可执行文件
- **Windows** - `web-novel-downloader.exe`
- **macOS** - `web-novel-downloader`
- **Linux** - `web-novel-downloader`（需要Linux系统构建）

## 🔧 开发工具

### 代码质量
- **black** - 代码格式化
- **flake8** - 代码检查
- **mypy** - 类型检查
- **pytest** - 测试框架

### 构建工具
- **setuptools** - Python包构建
- **build** - 现代构建工具
- **PyInstaller** - 可执行文件生成

## 📦 模块说明

### 核心模块

#### `core.py` - 核心逻辑
- `NovelDownloader` 类：主要的小说下载器
- 支持XPath解析、并发下载、内容处理
- 内置反爬虫检测和Cloudflare保护处理
- 支持Chrome路径配置和浏览器控制

#### `cli.py` - 命令行接口
- 解析命令行参数
- 提供 `parse`、`download`、`replace`、`merge` 命令
- 新增 `task` 和 `config validate` 命令
- 统一的错误处理和用户界面

#### `metadata.py` - 元数据管理
- 章节信息的保存和加载
- 元数据哈希生成和管理
- 支持断点续传

#### `epub_generator.py` - EPUB生成
- 生成标准EPUB格式电子书
- 支持目录导航和元数据

#### `utils.py` - 工具函数
- 字符串替换功能
- 章节排序和合并
- 文件处理工具

### 配置系统模块

#### `config_manager.py` - 配置管理器
- 加载和验证JSON配置文件
- 配置缓存机制
- 自动生成文件路径
- Chrome路径验证

#### `config_validator.py` - 配置验证器
- 验证JSON配置文件的格式和内容
- 检查必需字段和数据类型
- 业务规则验证（URL格式、XPath等）
- 详细的错误报告

#### `task_executor.py` - 任务执行器
- 执行完整的工作流程
- 四步工作流程：parse → download → replace → merge
- 智能跳过已存在的元数据文件
- 完善的错误处理和进度显示

### 配置文件

#### `configs/` 目录
- 存储JSON配置文件
- 每个配置文件对应一个下载任务
- 支持多个网站和小说配置

## 📋 配置文件说明

### pyproject.toml
现代Python项目配置文件，包含：
- 项目元数据
- 依赖管理
- 构建配置
- 工具配置（black, mypy, pytest等）

### setup.py
传统Python包配置文件，用于：
- 向后兼容
- 复杂构建需求
- 自定义安装逻辑

### MANIFEST.in
指定包含在源码包中的额外文件：
- README.md
- LICENSE
- 配置文件
- 文档文件

## 🚀 部署和分发

### 开发者
```bash
# 安装开发版本
pip install -e ".[dev]"

# 运行测试
python -m pytest tests/ -v

# 构建包
python scripts/build/build.py --packages
```

### 最终用户
```bash
# 安装Python包
pip install dist/web_novel_downloader-1.0.0-py3-none-any.whl

# 或使用可执行文件
./dist/web-novel-downloader --help
```

## 📚 文档结构

- **README.md** - 项目概述和快速开始
- **USAGE_GUIDE.md** - 详细使用说明
- **QUICK_START.md** - 快速开始指南
- **PROJECT_STRUCTURE.md** - 项目结构说明（本文件）
- **spec/develop-logs/** - 开发日志和进度记录

## ✅ 最佳实践

1. **遵循PEP 518** - 使用 `pyproject.toml` 作为主要配置文件
2. **保持向后兼容** - 同时提供 `setup.py` 和 `pyproject.toml`
3. **自动化构建** - 使用 Makefile 和脚本自动化构建过程
4. **文档驱动** - 保持文档与代码同步更新
5. **版本控制** - 使用语义化版本控制
6. **测试覆盖** - 保持高测试覆盖率
7. **代码质量** - 使用工具确保代码质量
