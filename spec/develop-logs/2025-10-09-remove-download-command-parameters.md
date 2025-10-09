# 移除download命令中的特定参数

## 任务概述
为使命令的功能范围划分的更加清楚，需要从download命令中删除以下参数：
- `string-replacements`
- `chapter-pagination-xpath`
- `chapter-list-pagination-xpath`
- `force-parse`

## 任务目标
1. 从CLI参数定义中移除这些参数
2. 从download命令的执行逻辑中移除对这些参数的处理
3. 更新相关文档以反映这些变化

## 技术分析
这些参数的功能应该通过以下方式实现：
- `string-replacements`: 通过独立的`replace`命令处理
- `chapter-pagination-xpath` 和 `chapter-list-pagination-xpath`: 在`parse`命令中设置，download命令只使用存储的元数据
- `force-parse`: 功能重复，download命令应该完全基于元数据工作

## 实施计划
1. 修改`src/book_downloader/cli.py`中的参数定义
2. 修改`execute_download_command`函数，移除对这些参数的处理
3. 更新文档以反映变化
4. 测试确保功能正常

## 进度记录
- [x] 创建任务日志文件
- [x] 分析当前代码结构
- [x] 移除CLI参数定义
- [x] 修改执行逻辑
- [x] 更新文档
- [x] 测试验证

## 完成总结
成功完成了download命令参数清理任务：

### 已移除的参数
- `--string-replacements`: 字符串替换功能现在通过独立的`replace`命令处理
- `--chapter-pagination-xpath`: 章节分页XPath现在只在`parse`命令中设置
- `--chapter-list-pagination-xpath`: 章节列表分页XPath现在只在`parse`命令中设置  
- `--force-parse`: 强制解析功能已移除，download命令完全基于元数据工作

### 修改的文件
1. `src/book_downloader/cli.py`: 移除了download命令的参数定义和相关处理逻辑
2. `docs/USAGE_GUIDE.md`: 更新了download命令的文档，移除了已删除参数的说明
3. `README.md`: 更新了download命令的示例和参数说明

### 功能验证
- ✅ download命令现在只包含必要的参数：`--content-regex`, `--concurrency`, `--proxy`
- ✅ parse命令保留了所有必要的参数，包括分页和字符串替换设置
- ✅ replace命令保留了字符串替换功能
- ✅ 所有命令的help输出都正确显示

### 设计理念
通过这次清理，实现了更清晰的功能分离：
- **parse命令**: 负责解析和配置，设置所有必要的XPath和替换规则
- **download命令**: 专注于下载，完全基于元数据工作
- **replace命令**: 专门处理下载后的内容替换

这样的设计使得每个命令的职责更加明确，用户使用起来也更加直观。
