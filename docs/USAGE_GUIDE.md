# 小说下载器完整使用指南

本指南详细说明如何使用小说下载器工具，从网站下载小说章节，进行内容处理，并生成最终文件。

## 📋 工作流程概述

1. **解析章节**：使用 `parse` 命令解析网站章节列表，生成包含章节名称和URL的JSON文件
2. **下载内容**：使用 `download` 命令并发下载章节内容（基于已保存的元数据）
3. **内容处理**：使用 `replace` 命令对下载的章节内容进行文本替换
4. **合并文件**：使用 `merge` 命令将处理后的章节合并为TXT或EPUB文件

> **💡 提示**：`download` 命令完全基于 `parse` 命令生成的元数据，无需重复提供URL和XPath参数。这种设计提高了使用效率并减少了错误。

## 📋 使用前准备

### 技能要求

使用本工具需要具备以下基础知识：

- **XPath基础**：能够编写XPath表达式来定位HTML元素
- **HTML基础**：理解HTML结构，能够识别网页元素
- **浏览器开发者工具**：会使用F12开发者工具检查元素结构
- **Python基础**：具备基本的Python命令行使用能力

> **💡 提示**：如果不熟悉XPath，建议先学习XPath语法。可以使用浏览器开发者工具的Console标签测试XPath表达式：`$x("your-xpath-here")`

### XPath学习资源

- [W3Schools XPath教程](https://www.w3schools.com/xml/xpath_intro.asp)
- [MDN XPath文档](https://developer.mozilla.org/en-US/docs/Web/XPath)
- 浏览器开发者工具中的XPath测试功能

## 🚀 安装和准备

### 安装依赖

#### 方法一：使用requirements.txt（推荐）
```bash
pip install -r requirements.txt
```

#### 方法二：安装为开发包
```bash
pip install -e .
```

#### 方法三：安装生产包
```bash
pip install .
```

#### 开发依赖（可选）
如果需要运行测试或进行开发，可以安装开发依赖：
```bash
pip install -e ".[dev]"
```

### 命令行工具

项目提供了两种使用方式：

#### 方式一：直接使用脚本（推荐）
```bash
python scripts/book_downloader.py <command> [options]
```

#### 方式二：安装为包后使用
```bash
# 安装包
pip install -e .

# 使用命令行工具
web-novel-downloader <command> [options]
```

### 可用命令

- `parse`：解析章节列表，提取章节链接和标题
- `download`：下载章节内容（基于已保存的元数据）
- `replace`：对下载的章节进行字符串替换
- `merge`：将章节合并为TXT或EPUB文件

## 第一步：解析章节列表 (parse)

### 基本用法

```bash
python scripts/book_downloader.py parse --menu-url "<网站URL>" --chapter-xpath "<XPath表达式>" --content-xpath "<XPath表达式>"
```

### 必需参数

- `--menu-url`：小说目录页URL
- `--chapter-xpath`：章节链接的XPath表达式（匹配`<a>`标签）
- `--content-xpath`：章节内容的XPath表达式

### 可选参数

- `--chapter-pagination-xpath`：章节内分页的XPath表达式
- `--chapter-list-pagination-xpath`：章节列表分页的XPath表达式
- `--content-regex`：内容过滤的正则表达式
- `--string-replacements`：字符串替换规则（JSON格式）
- `--proxy`：代理服务器地址

### 示例

```bash
python scripts/book_downloader.py parse \
  --menu-url "https://www.example.com/book/123456" \
  --chapter-xpath "(//div[@class='bd'])[2]//ul[@class='list']//li/a" \
  --content-xpath "//div[@class='page-content']" \
  --chapter-list-pagination-xpath "//a[contains(text(),'下一页')]" \
  --string-replacements '["<img src=\"/path/to/image.png\">", "replacement"]'
```

### 输出

命令执行后会：
1. 解析章节列表，提取章节名称和URL
2. 将信息保存到 `chapters/metadata/chapters_<hash>.json` 文件
3. 显示解析的章节数量和前几个章节信息

**示例输出：**
```
📋 Parsing chapters from: https://www.example.com/book/123456
Found 95 chapters on page 1
📋 Saved chapter metadata to: chapters/metadata/chapters_879584cc.json
✅ Chapter parsing completed: 95 chapters found
```

## 第二步：下载章节内容 (download)

### 基本用法

```bash
python scripts/book_downloader.py download
```

### 可选参数

- `--concurrency N`：并发下载数量（默认3）
- `--proxy <proxy>`：代理服务器（如：127.0.0.1:10808）
- `--content-regex`：内容过滤的正则表达式（覆盖元数据中的设置）
- `--string-replacements`：字符串替换规则（覆盖元数据中的设置）
- `--chapter-pagination-xpath`：章节内分页的XPath表达式（覆盖元数据中的设置）
- `--chapter-list-pagination-xpath`：章节列表分页的XPath表达式（覆盖元数据中的设置）
- `--force-parse`：强制重新解析，即使存在元数据

### 示例

```bash
python scripts/book_downloader.py download --concurrency 5
```

### 功能特性

- **基于元数据**：完全基于parse命令生成的元数据进行下载
- **并发下载**：同时下载多个章节，提高效率
- **断点续传**：自动跳过已下载的章节
- **分页支持**：处理跨多页的章节内容
- **Cloudflare保护**：自动检测并处理反爬虫保护
- **错误处理**：详细的错误日志和恢复机制
- **参数覆盖**：支持在下载时覆盖元数据中的设置

### 输出

命令执行后会：
1. 读取之前保存的章节元数据
2. 并发下载章节内容到 `chapters/` 目录
3. 显示下载进度和统计信息

**示例输出：**
```
📖 Loading stored chapters from metadata...
📖 Found 95 stored chapters
🚀 Starting download with 5 concurrent workers...
✅ Download completed: 95 chapters processed (90 downloaded, 5 skipped)
```

## 第三步：内容替换处理 (replace)

### 基本用法

```bash
python scripts/book_downloader.py replace --string-replacements "[['old1','new1'],['old2','new2']]"
```

### 命令选项

- `--string-replacements`：字符串替换规则（JSON格式，必需）
- `--regex-replacements`：正则表达式替换规则（JSON格式，可选）
- `--case-sensitive`：字符串替换是否区分大小写（默认不区分）
- `--backup`：替换前创建备份文件
- `--dry-run`：预览模式，不实际替换
- `--pattern`：文件匹配模式（默认：*.html）

### 使用示例

#### 1. 基本字符串替换

替换图片标签为指定文本（需要转义时，内层用双引号，最外层用单引号）：

```bash
python scripts/book_downloader.py replace \
  --string-replacements '[["Hello","Hi"],["hello","hi"]，["<img src=\"/path/to/image.png\">", "replacement"]]'
```

#### 2. 预览模式（推荐先使用）

预览替换效果而不实际修改文件：

```bash
python scripts/book_downloader.py replace \
  --string-replacements '[["Hello","Hi"],["hello","hi"]，["<img src=\"/path/to/image.png\">", "replacement"]]' \
  --dry-run
```

#### 3. 创建备份

替换前创建备份文件：

```bash
python scripts/book_downloader.py replace \
  --string-replacements '[["Hello","Hi"],["hello","hi"]，["<img src=\"/path/to/image.png\">", "replacement"]]' \
  --backup
```

#### 4. 清理HTML标签

清理不需要的HTML标签：

```bash
python scripts/book_downloader.py replace \
  --string-replacements '[["<p>",""],["</p>",""],["<br>","\\n"],["<div>",""],["</div>",""]]'
```

#### 5. 正则表达式替换

使用正则表达式进行复杂替换：

```bash
python scripts/book_downloader.py replace \
  --regex-replacements '[["<img[^>]*src=\"[^\"]*\"[^>]*>", "[IMAGE]"], ["\\s+", " "]]'
```

#### 6. 处理特定文件

只处理特定模式的文件：

```bash
python scripts/book_downloader.py replace \
  --string-replacements "[['old','new']]" \
  --pattern "chapter_*.html"
```

### JSON格式说明

#### 字符串替换格式
```json
[["old_string1", "new_string1"], ["old_string2", "new_string2"]]
```

#### 正则表达式替换格式
```json
[["pattern1", "replacement1"], ["pattern2", "replacement2"]]
```

### 重要注意事项

1. **JSON转义**：在替换字符串中使用双引号时，需要用反斜杠转义：
   ```json
   [["<img src=\"/path/to/image.png\">", "replacement"]]
   ```

2. **大小写敏感**：默认字符串替换不区分大小写，使用 `--case-sensitive` 进行精确匹配

3. **备份文件**：使用 `--backup` 时，原文件保存在 `chapters/backup/backup_YYYYMMDD_HHMMSS/` 目录

4. **文件模式**：`--pattern` 选项使用glob模式匹配文件（如：`*.html`、`chapter_*.html`）

### 输出示例

```
🔍 Processing chapters with replace command...
📁 Found 95 files matching pattern: *.html
🔄 Processing: Chapter（01-05）.html
  ✅ Modified: Chapter（01-05）.html
🔄 Processing: Chapter（06-10）.html
  ✅ Modified: Chapter（06-10）.html
...
📊 Summary: 95 files processed, 95 files modified
```

## 第四步：合并文件 (merge)

### 基本用法

```bash
python scripts/book_downloader.py merge --output "<文件名>" --title "<标题>"
```

### 命令选项

- `--output`：输出文件名（必需）
- `--title`：小说标题（默认：Downloaded Novel）
- `--format`：输出格式 - `txt` 或 `epub`（默认：txt）
- `--author`：作者名称（EPUB格式需要）
- `--reverse`：按倒序合并章节（默认：正序）

### 使用示例

#### 1. 生成TXT文件

```bash
python scripts/book_downloader.py merge --output "my_novel.txt" --title "我的小说"
```

#### 2. 生成EPUB文件

```bash
python scripts/book_downloader.py merge --format epub --output "my_novel.epub" --title "我的小说" --author "作者名"
```

#### 3. 按倒序合并章节

```bash
python scripts/book_downloader.py merge --output "my_novel.txt" --title "我的小说" --reverse
```

### 输出格式说明

#### TXT格式
- 纯文本格式
- 章节标题和内容按顺序排列
- 适合文本阅读器

#### EPUB格式
- 标准电子书格式
- 包含目录导航
- 支持各种电子书阅读器
- 章节标题使用真实名称而非ID

### 输出示例

```
📚 Merging 95 chapters into my_novel.epub...
Creating EPUB chapter: Chapter（01-05）.html
Creating EPUB chapter: Chapter（06-10）.html
...
✅ Novel merged successfully: my_novel.epub
```

## 🔧 XPath表达式指南

### 常见XPath模式

#### 章节链接XPath

**列表格式：**
```xpath
//ul[@class="chapter-list"]//a
```

**表格格式：**
```xpath
//table//a[contains(@href, 'chapter')]
```

**特定容器：**
```xpath
//div[@id="catalog"]//li/a
```

#### 章节内容XPath

**基本内容：**
```xpath
//div[@class="content"]
```

**排除广告：**
```xpath
//div[@class="content"]//text()[not(ancestor::script) and not(ancestor::div[@class="ad"])]
```

**特定容器：**
```xpath
//div[@class="txtnav"]
```

### XPath测试方法

1. 在浏览器中打开目标页面
2. 按F12打开开发者工具
3. 切换到Console标签
4. 输入：`$x("your-xpath-here")`
5. 按回车查看匹配的元素

## 🛠️ 高级功能

### 分页支持

#### 章节内分页
处理跨多页的章节内容：

```bash
python scripts/book_downloader.py parse \
  --menu-url "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter']" \
  --content-xpath "//div[@class='content']" \
  --chapter-pagination-xpath "//a[contains(text(),'下一页')]"
```

#### 章节列表分页
处理多页的章节列表：

```bash
python scripts/book_downloader.py parse \
  --menu-url "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter']" \
  --content-xpath "//div[@class='content']" \
  --chapter-list-pagination-xpath "//a[contains(text(),'下一页')]"
```

### 内容过滤

使用正则表达式过滤内容：

```bash
python scripts/book_downloader.py parse \
  --menu-url "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter']" \
  --content-xpath "//div[@class='content']" \
  --content-regex "第.*?章.*?$"
```

### 批量处理脚本

创建脚本批量下载多本小说：

```bash
#!/bin/bash
# download_multiple_novels.sh

novels=(
    "https://site1.com/novel1/|//div[@class='chapters']//a|//div[@class='content']"
    "https://site2.com/novel2/|//ul[@class='chapter-list']//a|//div[@id='text']"
)

for novel in "${novels[@]}"; do
    IFS='|' read -r url chapter_xpath content_xpath <<< "$novel"
    echo "Processing: $url"
    
    # Parse chapters
    python scripts/book_downloader.py parse \
        --menu-url "$url" \
        --chapter-xpath "$chapter_xpath" \
        --content-xpath "$content_xpath"
    
    # Download chapters
    python scripts/book_downloader.py download
    
    # Replace content if needed
    python scripts/book_downloader.py replace \
        --string-replacements "[['<img[^>]*>','[IMAGE]']]"
    
    # Merge to EPUB
    python scripts/book_downloader.py merge \
        --format epub \
        --output "$(basename "$url").epub" \
        --title "$(basename "$url")"
done
```

## 🔍 故障排除

### 常见问题

1. **没有找到章节**：
   - 检查章节XPath表达式是否正确
   - 使用浏览器开发者工具测试XPath

2. **内容提取失败**：
   - 检查content-xpath是否正确
   - 尝试更简单的XPath表达式

3. **浏览器错误**：
   - 尝试降低并发数量
   - 使用代理服务器

4. **权限错误**：
   - 确保对项目目录有写权限

5. **Cloudflare保护**：
   - 脚本会自动检测并等待手动验证
   - 在浏览器中完成验证后脚本会自动继续

6. **元数据问题**：
   - 确保先运行 `parse` 命令生成元数据
   - 检查 `chapters/metadata/` 目录是否存在JSON文件
   - 使用 `--force-parse` 强制重新解析

7. **脚本路径问题**：
   - 确保在项目根目录下运行命令
   - 使用 `python scripts/book_downloader.py` 而不是 `python novel_downloader.py`

### Cloudflare保护处理

脚本会自动检测Cloudflare保护：

1. **自动检测**：检测页面标题包含以下内容：
   - "请稍候…"（中文）
   - "Just a moment..."（英文）
   - "Checking your browser..."（英文）

2. **手动验证**：检测到保护时：
   - 脚本会暂停并显示消息
   - 浏览器窗口保持打开供手动验证
   - 完成验证（点击复选框、解决验证码等）
   - 验证完成后脚本自动继续

3. **超时处理**：如果验证超过60秒，脚本会继续并显示警告

**示例输出：**
```
⚠️  Cloudflare protection detected on chapter '第1章 开端'
   Page title: Just a moment...
   Please manually complete the verification in the browser window.
   The script will wait for you to complete the verification...
   Waiting for verification... (2s/60s)
   ✅ Verification completed! Continuing...
```

### 性能优化建议

- 从低并发数开始（1-3），逐步增加
- 使用具体的XPath表达式避免匹配不需要的元素
- 监控系统资源使用情况
- 考虑使用代理服务器提高某些地区的性能

### 调试技巧

1. **使用dry-run模式**：
```bash
python scripts/book_downloader.py replace --string-replacements "[['old','new']]" --dry-run
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

4. **强制重新解析**：
```bash
python scripts/book_downloader.py download --force-parse
```

## 📊 完整工作流程示例

以下是一个完整的使用示例：

```bash
# 1. 解析章节列表
python scripts/book_downloader.py parse \
  --menu-url "https://www.example.com/book/123456" \
  --chapter-xpath "(//div[@class='bd'])[2]//ul[@class='list']//li/a" \
  --content-xpath "//div[@class='page-content']" \
  --chapter-list-pagination-xpath "//a[contains(text(),'下一页')]"

# 2. 下载章节内容
python scripts/book_downloader.py download \
  --concurrency 5

# 3. 替换图片标签为文字（预览模式）
python scripts/book_downloader.py replace \
  --string-replacements '["<img src=\"/path/to/image.png\">", "replacement"]' \
  --dry-run

# 4. 实际替换（创建备份）
python scripts/book_downloader.py replace \
  --string-replacements '["<img src=\"/path/to/image.png\">", "replacement"]' \
  --backup

# 5. 清理HTML标签
python scripts/book_downloader.py replace \
  --string-replacements "[['<p>',''],['</p>',''],['<br>','\\n']]"

# 6. 生成EPUB文件
python scripts/book_downloader.py merge \
  --format epub \
  --output "noval.epub" \
  --title "noval" \
  --author "作者名"
```

## 📝 注意事项

1. **遵守网站规则**：请遵守网站的robots.txt和使用条款
2. **合理使用**：避免过于频繁的请求，以免给服务器造成压力
3. **备份重要数据**：使用replace命令时建议先创建备份
4. **测试XPath**：在实际使用前，建议先用浏览器开发者工具测试XPath表达式
5. **检查输出**：使用dry-run模式预览替换效果

---

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

### 技能要求提醒

使用本工具前，请确保您已具备：
- XPath表达式编写能力
- HTML结构理解能力
- 浏览器开发者工具使用能力
- 基本Python命令行操作能力

**请在使用前仔细阅读并同意以上条款。**

---

通过以上完整的工作流程，您可以高效地下载、处理和合并小说内容，生成高质量的电子书文件。
