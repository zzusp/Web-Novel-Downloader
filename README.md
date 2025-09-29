# Web小说下载器 (Web Novel Downloader)

一个功能强大的Web小说下载工具，支持从网站批量下载小说章节，并提供多种输出格式。

> **🔄 最新更新**：项目已重构为模块化架构，提高了代码的可读性和可维护性。所有功能保持不变，使用方式完全兼容。

## ✨ 主要功能

- **智能章节解析**：使用XPath表达式精确提取章节链接和内容
- **并发下载**：支持多线程并发下载，提高效率
- **分页支持**：
  - 章节内分页：处理跨多页的章节内容
  - 章节列表分页：支持多页章节列表的自动翻页
- **内容处理**：
  - 正则表达式过滤
  - 字符串替换（支持图片标签替换为文字）
  - 内容清理和格式化
- **多种输出格式**：
  - TXT：纯文本格式
  - EPUB：标准电子书格式，支持目录导航
- **元数据管理**：自动保存和加载章节信息
- **断点续传**：跳过已下载的章节
- **Cloudflare保护处理**：自动处理反爬虫保护

---

## 🚀 快速开始（普通用户）

### 下载可执行文件

项目提供了预构建的可执行文件，无需安装Python环境即可使用：

#### Windows版本
- **文件**: `dist/web-novel-downloader.exe`
- **大小**: 约15MB
- **要求**: Windows 10/11
- **使用**: 双击运行或命令行调用

#### macOS版本
- **文件**: `dist/web-novel-downloader.app`
- **大小**: 约15MB
- **要求**: macOS 10.14+
- **使用**: 双击运行或命令行调用

### 基本使用步骤

#### 1. 解析章节列表
```bash
# Windows
./web-novel-downloader.exe parse --menu-url "https://example.com/novel" --chapter-xpath "//a[@class='chapter-link']" --content-xpath "//div[@class='content']"

# macOS
./web-novel-downloader.app/Contents/MacOS/web-novel-downloader parse --menu-url "https://example.com/novel" --chapter-xpath "//a[@class='chapter-link']" --content-xpath "//div[@class='content']"
```

#### 2. 下载章节
```bash
# Windows
./web-novel-downloader.exe download --concurrency 5

# macOS
./web-novel-downloader.app/Contents/MacOS/web-novel-downloader download --concurrency 5
```

#### 3. 章节内容字符串替换（可选）
```bash
# Windows
./web-novel-downloader.exe replace --string-replacements "[['<p>',''],['</p>',''],['<div>',''],['</div>','']]"

# macOS
./web-novel-downloader.app/Contents/MacOS/web-novel-downloader replace --string-replacements "[['<p>',''],['</p>',''],['<div>',''],['</div>','']]"
```

#### 4. 合并为TXT文件
```bash
# Windows
./web-novel-downloader.exe merge --format txt --output "my_novel.txt" --title "小说标题"

# macOS
./web-novel-downloader.app/Contents/MacOS/web-novel-downloader merge --format txt --output "my_novel.txt" --title "小说标题"
```

#### 5. 合并为EPUB文件
```bash
# Windows
./web-novel-downloader.exe merge --format epub --output "my_novel.epub" --title "小说标题" --author "作者名"

# macOS
./web-novel-downloader.app/Contents/MacOS/web-novel-downloader merge --format epub --output "my_novel.epub" --title "小说标题" --author "作者名"
```

### 详细使用说明

#### 解析章节 (parse)

解析网站上的章节列表，提取章节链接和标题。

**必需参数**：
- `--menu-url`：小说目录页URL
- `--chapter-xpath`：章节链接的XPath表达式
- `--content-xpath`：章节内容的XPath表达式

**可选参数**：
- `--chapter-pagination-xpath`：章节内分页的XPath表达式
- `--chapter-list-pagination-xpath`：章节列表分页的XPath表达式
- `--content-regex`：内容过滤的正则表达式
- `--string-replacements`：字符串替换规则（JSON格式）
- `--proxy`：代理服务器地址

**示例**：
```bash
./web-novel-downloader.exe parse \
  --menu-url "https://www.example.com/book/123456" \
  --chapter-xpath "(//div[@class='bd'])[2]//ul[@class='list']//li/a" \
  --content-xpath "//div[@class='page-content']" \
  --chapter-list-pagination-xpath "//a[contains(text(),'下一页')]" \
  --string-replacements "[['<p>',''],['</p>',''],['<div>',''],['</div>','']]"
```

#### 下载章节 (download)

使用已保存的元数据下载章节内容。

> **💡 说明**：此命令完全基于parse命令生成的元数据，无需提供URL或XPath参数。

**可选参数**：
- `--concurrency`：并发下载数量（默认3）
- `--proxy`：代理服务器地址
- `--content-regex`：内容过滤的正则表达式（覆盖元数据中的设置）
- `--string-replacements`：字符串替换规则（覆盖元数据中的设置）
- `--chapter-pagination-xpath`：章节内分页的XPath表达式（覆盖元数据中的设置）
- `--chapter-list-pagination-xpath`：章节列表分页的XPath表达式（覆盖元数据中的设置）
- `--force-parse`：强制重新解析，即使存在元数据

**示例**：
```bash
# 使用元数据下载（推荐）
./web-novel-downloader.exe download

# 指定并发数量
./web-novel-downloader.exe download --concurrency 5

# 覆盖字符串替换规则
./web-novel-downloader.exe download --string-replacements "[['<p>',''],['</p>','']]"
```

#### 合并章节 (merge)

将下载的章节合并为单个文件。

**必需参数**：
- `--output`：输出文件名

**可选参数**：
- `--format`：输出格式（txt/epub，默认txt）
- `--title`：小说标题
- `--author`：作者名称（EPUB格式需要）

**示例**：
```bash
# 生成TXT文件
./web-novel-downloader.exe merge --format txt --output "my_novel.txt" --title "我的小说"

# 生成EPUB文件
./web-novel-downloader.exe merge --format epub --output "my_novel.epub" --title "我的小说" --author "作者名"
```

#### 字符串替换 (replace)

对已下载的章节文件进行字符串替换。

**必需参数**：
- `--string-replacements`：替换规则（JSON格式）

> **💡 JSON格式说明**：支持两种格式：
> - 单引号格式：`[['old1','new1'],['old2','new2']]`
> - 双引号格式：`[["old1","new1"],["old2","new2"]]`

**可选参数**：
- `--regex-replacements`：正则表达式替换规则
- `--case-sensitive`：是否区分大小写（默认False）
- `--backup`：是否创建备份文件
- `--dry-run`：预览模式，不实际修改文件
- `--pattern`：文件匹配模式（默认*.html）

**示例**：
```bash
# 基本字符串替换（单引号格式）
./web-novel-downloader.exe replace --string-replacements "[['<p>',''],['</p>','']]"

# 基本字符串替换（双引号格式）
./web-novel-downloader.exe replace --string-replacements "[[\"<p>\",\"\"],[\"</p>\",\"\"],[\"<br>\",\"\\n\"]]"

# 预览模式
./web-novel-downloader.exe replace --string-replacements "[['old','new']]" --dry-run

# 正则表达式替换
./web-novel-downloader.exe replace --regex-replacements "[['<img[^>]*>','[IMAGE]']]"

# 创建备份
./web-novel-downloader.exe replace --string-replacements "[['old','new']]" --backup
```

### 高级功能

#### 分页支持

**章节内分页**：处理跨多页的章节内容
```bash
./web-novel-downloader.exe parse \
  --menu-url "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter']" \
  --content-xpath "//div[@class='content']" \
  --chapter-pagination-xpath "//a[contains(text(),'下一页')]"
```

**章节列表分页**：处理多页的章节列表
```bash
./web-novel-downloader.exe parse \
  --menu-url "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter']" \
  --content-xpath "//div[@class='content']" \
  --chapter-list-pagination-xpath "//a[contains(text(),'下一页')]"
```

#### 内容过滤

使用正则表达式过滤内容：
```bash
./web-novel-downloader.exe parse \
  --menu-url "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter']" \
  --content-xpath "//div[@class='content']" \
  --content-regex "第.*?章.*?$"
```

#### 字符串替换

支持复杂的字符串替换规则：
```bash
# 清理HTML标签
./web-novel-downloader.exe replace \
  --string-replacements "[['<p>',''],['</p>',''],['<div>',''],['</div>','']]"
```

### 🔍 故障排除

#### 常见问题

1. **Cloudflare保护**：
   - 程序会自动处理Cloudflare保护
   - 如果遇到问题，请等待几分钟后重试

2. **XPath表达式错误**：
   - 使用浏览器开发者工具检查元素结构
   - 确保XPath表达式正确匹配目标元素

3. **内容提取失败**：
   - 检查content-xpath是否正确
   - 尝试更简单的XPath表达式

4. **EPUB文件问题**：
   - 确保使用支持EPUB的阅读器
   - 检查文件是否完整下载

#### 调试技巧

1. **使用dry-run模式**：
```bash
./web-novel-downloader.exe replace --string-replacements "[['old','new']]" --dry-run
```

2. **检查元数据**：
```bash
ls chapters/metadata/
cat chapters/metadata/*.json
```

3. **查看章节文件**：
```bash
ls chapters/
head -20 chapters/*.html
```

---

## 🛠️ 开发者指南

### 技能要求

使用本工具进行开发需要具备以下基础知识：

- **XPath基础**：能够编写XPath表达式来定位HTML元素
- **HTML基础**：理解HTML结构，能够识别网页元素
- **浏览器开发者工具**：会使用F12开发者工具检查元素结构
- **Python基础**：具备基本的Python命令行使用能力

> **💡 提示**：如果不熟悉XPath，建议先学习XPath语法。可以使用浏览器开发者工具的Console标签测试XPath表达式：`$x("your-xpath-here")`

### 开发环境设置

#### 安装依赖

```bash
pip install -e .
```

#### 开发模式安装

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 或使用构建脚本
python scripts/build/build.py --help
```

### 使用Python包

#### 方法一：使用脚本

1. **解析章节列表**：
```bash
python scripts/book_downloader.py parse --menu-url "https://example.com/novel" --chapter-xpath "//a[@class='chapter-link']" --content-xpath "//div[@class='content']"
```

2. **下载章节**：
```bash
python scripts/book_downloader.py download --concurrency 5
```

3. **章节内容字符串替换（可选）**：
```bash
python scripts/book_downloader.py replace --string-replacements "[['<p>',''],['</p>',''],['<div>',''],['</div>','']]"
```

4. **合并为TXT文件**：
```bash
python scripts/book_downloader.py merge --format txt --output "my_novel.txt" --title "小说标题"
```

5. **合并为EPUB文件**：
```bash
python scripts/book_downloader.py merge --format epub --output "my_novel.epub" --title "小说标题" --author "作者名"
```

#### 方法二：安装为包后使用

1. **安装包**：
```bash
pip install -e .
```

2. **使用命令行工具**：
```bash
web-novel-downloader parse --menu-url "https://example.com/novel" --chapter-xpath "//a[@class='chapter-link']" --content-xpath "//div[@class='content']"
web-novel-downloader download --concurrency 5
web-novel-downloader merge --format epub --output "my_novel.epub" --title "小说标题" --author "作者名"
```

#### 方法三：作为Python包使用

```python
from book_downloader import NovelDownloader

# 创建下载器实例
downloader = NovelDownloader(
    chapter_xpath="//a[@class='chapter-link']",
    content_xpath="//div[@class='content']",
    concurrency=5
)

# 下载小说
import asyncio
asyncio.run(downloader.download_novel("https://example.com/novel"))
```

### 开发工具

#### 运行测试

```bash
pytest
```

#### 代码格式化

```bash
black src/ tests/ scripts/
```

#### 类型检查

```bash
mypy src/
```

### 构建和安装

#### 构建包
```bash
# 使用构建脚本（推荐）
python scripts/build/build.py --packages

# 或手动构建
python -m build
```

#### 构建可执行文件
```bash
# 使用构建脚本（推荐）
python scripts/build/build.py --exe windows

# 或手动构建
pyinstaller build_win.spec --clean

# 构建所有内容
python scripts/build/build.py --all
```

#### 安装包
```bash
# 从构建的包安装
pip install dist/book_downloader-1.0.0-py3-none-any.whl

# 或从源码安装
pip install .
```

### 项目架构

#### 技术特性

- **模块化架构**：代码拆分为多个模块，提高可读性和可维护性
- **异步处理**：使用asyncio实现高效的异步下载
- **浏览器自动化**：基于pydoll的浏览器自动化，支持JavaScript渲染
- **XPath解析**：使用lxml进行精确的HTML解析
- **EPUB标准**：完全符合EPUB 2.0标准，支持各种电子书阅读器
- **错误处理**：完善的错误处理和恢复机制
- **进度显示**：详细的下载进度和状态显示
- **元数据管理**：智能的章节信息存储和检索
- **跨平台构建**：支持Windows和macOS可执行文件构建
- **智能构建系统**：自动回退机制，确保构建成功

#### 依赖包

- `pydoll-python`：浏览器自动化
- `lxml`：HTML/XML解析
- `asyncio`：异步编程支持（Python内置）

#### 模块架构

项目采用模块化设计，将原来的单一文件拆分为多个功能模块：

- **`config.py`**：配置和常量管理
- **`utils.py`**：通用工具函数
- **`metadata.py`**：章节元数据管理
- **`epub_generator.py`**：EPUB文件生成
- **`core.py`**：核心下载功能（NovelDownloader类）
- **`cli.py`**：命令行接口和参数解析
- **`novel_downloader.py`**：主入口文件

这种设计提高了代码的可读性、可维护性和可扩展性。详细说明请参考 [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)。

#### 项目结构

```
book-downloader/
├── src/                    # 源代码目录
│   └── book_downloader/   # 主包
│       ├── __init__.py    # 包初始化文件
│       ├── config.py      # 配置和常量
│       ├── utils.py       # 工具函数
│       ├── metadata.py    # 元数据管理
│       ├── epub_generator.py # EPUB生成模块
│       ├── core.py        # 核心下载功能
│       ├── cli.py         # 命令行接口
│       └── scraper.py     # 基础爬虫模块
├── scripts/               # 可执行脚本
│   ├── book_downloader.py # 主入口脚本
│   └── scraper.py         # 爬虫脚本
├── tests/                 # 测试目录
│   ├── __init__.py
│   ├── conftest.py        # 测试配置
│   ├── test_utils.py      # 工具函数测试
│   └── test_config.py     # 配置测试
├── spec/                  # 项目规范文档
│   ├── develop-logs/      # 开发日志
│   └── development-progress.md
├── chapters/              # 章节文件目录
│   ├── metadata/         # 元数据存储
│   └── *.html           # 下载的章节文件
├── temp/                  # 临时文件目录
├── setup.py              # 安装脚本
├── pyproject.toml        # 现代Python项目配置
├── build_win.spec       # Windows PyInstaller配置
├── build_macos.spec     # macOS PyInstaller配置
├── README.md            # 说明文档
└── docs/                # 文档目录
    ├── QUICK_START.md   # 快速开始指南
    ├── USAGE_GUIDE.md   # 使用指南
    └── PROJECT_STRUCTURE.md # 项目结构说明
```

### 贡献

欢迎提交Issue和Pull Request来改进这个项目。

#### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

### 支持

如果您遇到问题或有建议，请：

1. 查看[快速开始指南](docs/QUICK_START.md)快速上手
2. 检查[使用指南](docs/USAGE_GUIDE.md)获取详细使用说明
3. 查看[项目结构](docs/PROJECT_STRUCTURE.md)了解项目架构
4. 提交Issue描述您的问题

---

## 📄 许可证

本项目采用MIT许可证。

## ⚠️ 免责声明

**本项目仅供学习和交流使用，严禁用于商业用途。**

### 使用须知

1. **学习目的**：本项目仅用于技术学习和个人研究
2. **禁止商用**：严禁将本项目用于任何商业用途
3. **遵守法律**：使用者需遵守当地法律法规和网站使用条款
4. **版权尊重**：请尊重原网站和作者的版权，仅下载个人学习使用
5. **风险自担**：使用本工具产生的任何后果由使用者自行承担

### 法律声明

- 本项目不承担因使用本工具而产生的任何法律责任
- 使用者应当遵守目标网站的robots.txt和使用条款
- 请合理使用，避免对目标网站造成过大负担
- 如涉及版权问题，请立即停止使用并删除相关内容

**请在使用前仔细阅读并同意以上条款。**