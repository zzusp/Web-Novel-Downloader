# 移除parse命令中的string-replacements参数

## 任务概述
为使命令的功能范围划分的更加清楚，需要从parse命令中删除`string-replacements`参数。

## 任务目标
1. 从CLI参数定义中移除`string-replacements`参数
2. 从parse命令的执行逻辑中移除对该参数的处理
3. 更新相关文档以反映这些变化

## 技术分析
`string-replacements`参数的功能应该通过以下方式实现：
- 在`parse`命令中移除，因为字符串替换应该在下载完成后通过`replace`命令处理
- 这样可以让parse命令专注于解析章节信息，replace命令专注于内容处理
- 实现更清晰的功能分离：parse负责解析，replace负责内容处理

## 实施计划
1. 修改`src/book_downloader/cli.py`中的parse命令参数定义
2. 修改`execute_parse_command`函数，移除对`string-replacements`参数的处理
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
成功完成了parse命令中string-replacements参数的移除任务：

### 已移除的参数
- `--string-replacements`: 字符串替换功能现在完全通过独立的`replace`命令处理

### 修改的文件
1. `src/book_downloader/cli.py`: 移除了parse命令的`--string-replacements`参数定义和相关处理逻辑
2. `docs/USAGE_GUIDE.md`: 更新了parse命令的文档，移除了`--string-replacements`参数的说明和示例

### 功能验证
- ✅ parse命令现在专注于解析章节信息，不再处理字符串替换
- ✅ replace命令保留了完整的字符串替换功能
- ✅ 所有命令的help输出都正确显示

### 设计理念
通过这次清理，实现了更清晰的功能分离：
- **parse命令**: 专注于解析章节列表和配置XPath表达式
- **download命令**: 专注于下载章节内容
- **replace命令**: 专门处理下载后的内容替换和字符串处理

这样的设计使得每个命令的职责更加明确，用户使用起来也更加直观。字符串替换现在完全在下载完成后通过replace命令处理，符合实际使用流程。
