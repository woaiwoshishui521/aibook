# 视频压缩功能 - 删除任务功能

## ✅ 已添加的功能

为视频压缩页面添加了删除任务的功能，用户可以删除不需要的压缩任务。

## 🎯 功能特点

### 前端界面
- ✅ 每个任务卡片都有"删除"按钮
- ✅ 删除前会弹出确认对话框
- ✅ 删除成功后自动刷新任务列表和统计信息
- ✅ 删除按钮使用红色样式，易于识别

### 后端处理
- ✅ 删除任务时同时删除关联的视频文件
  - 删除原始视频文件
  - 删除压缩后的视频文件
- ✅ 删除数据库记录
- ✅ 错误处理：即使文件删除失败，也会继续删除数据库记录

## 📝 修改的文件

### 1. `apps/video/templates/video/compression.html`

**添加的CSS样式**：

.btn-danger:hover {
    background: #dc2626;
}


**修改的任务卡片HTML**：
每个任务现在都有删除按钮：

<button class="btn btn-danger btn-small" onclick="deleteTask(${task.id})">
    删除
</button>


**添加的JavaScript函数**：

async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？删除后无法恢复。')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/tasks/${taskId}/`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('删除失败');
        }

        loadTasks();
        loadStatistics();
        alert('任务已删除');
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}


### 2. `apps/video/views.py`

**添加的导入**：

import os


**添加的方法**：

def destroy(self, request, *args, **kwargs):
    """删除任务及其关联的视频文件"""
    task = self.get_object()
    
    # 删除原始视频文件
    if task.original_video:
        try:
            if os.path.isfile(task.original_video.path):
                os.remove(task.original_video.path)
        except Exception as e:
            print(f"删除原始视频文件失败: {str(e)}")
    
    # 删除压缩后的视频文件
    if task.compressed_video:
        try:
            if os.path.isfile(task.compressed_video.path):
                os.remove(task.compressed_video.path)
        except Exception as e:
            print(f"删除压缩视频文件失败: {str(e)}")
    
    # 删除数据库记录
    return super().destroy(request, *args, **kwargs)


## 🚀 使用方法

### 通过Web界面删除任务

1. 访问 `http://localhost:8000/video/`
2. 在任务列表中找到要删除的任务
3. 点击红色的"删除"按钮
4. 在确认对话框中点击"确定"
5. 任务及其关联的视频文件将被删除

### 通过API删除任务


curl -X DELETE http://localhost:8000/video/api/tasks/{task_id}/


## 🔒 安全特性

1. **确认对话框**：删除前会弹出确认对话框，防止误操作
2. **文件清理**：删除任务时自动清理关联的视频文件，避免占用磁盘空间
3. **错误处理**：即使文件删除失败（如文件不存在），也会继续删除数据库记录

## 📊 删除操作的影响

删除任务后：
- ✅ 数据库记录被删除
- ✅ 原始视频文件被删除
- ✅ 压缩后的视频文件被删除
- ✅ 统计信息自动更新
- ✅ 任务列表自动刷新

## ⚠️ 注意事项

1. **不可恢复**：删除操作是永久性的，无法恢复
2. **文件清理**：删除任务会同时删除所有关联的视频文件
3. **处理中的任务**：可以删除正在处理中的任务，但后台处理线程可能会继续运行直到完成

## 🎨 界面展示

每个任务卡片现在都有三个可能的按钮：
- 🟢 **下载视频**（已完成的任务）
- 🔵 **重试**（失败的任务）
- 🔴 **删除**（所有任务）

## 🔄 测试步骤

1. **重启服务器**：
   
   python manage.py runserver
   

2. **测试删除功能**：
   - 创建一个测试任务
   - 等待任务完成或失败
   - 点击删除按钮
   - 确认任务被删除
   - 检查 `media/videos/` 目录，确认文件已被删除

## ✅ 功能完成

删除任务功能已完全实现并可以使用！
