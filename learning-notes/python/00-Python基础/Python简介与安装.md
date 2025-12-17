# Python简介与安装

## 1. Python简介

### 1.1 什么是Python

Python（英式发音：/ˈpaɪθən/；美式发音：/ˈpaɪθɑːn/）是由荷兰人吉多·范罗苏姆（Guido von Rossum）发明的一种编程语言，是目前世界上最受欢迎和拥有最多用户的编程语言。

### 1.2 Python编年史

1. **1989年12月**：吉多·范罗苏姆决心开发一个新的脚本语言及其解释器来打发无聊的圣诞节，新语言将作为 ABC 语言的继承者，主要用来替代 Unix shell 和 C 语言实现系统管理。由于吉多本人是 BBC 电视剧《*Monty Python's Flying Circus*》的忠实粉丝，所以他选择了 Python 这个词作为新语言的名字。

2. **1991年02月**：吉多·范罗苏姆在 alt.sources 新闻组上发布了 Python 解释器的最初代码，标记为版本0.9.0。

3. **1994年01月**：Python 1.0发布，梦开始的地方。

4. **2000年10月**：Python 2.0发布，Python 的整个开发过程更加透明，生态圈开始慢慢形成。

5. **2008年12月**：Python 3.0发布，引入了诸多现代编程语言的新特性，但并不完全向下兼容。

6. **2011年04月**：pip 首次发布，Python 语言有了自己的包管理工具。

7. **2018年07月**：吉多·范罗苏姆宣布从"终身仁慈独裁者"的职位上"永久休假"。

8. **2020年01月**：在 Python 2和 Python 3共存了11年之后，官方停止了对 Python 2的更新和维护，希望用户尽快切换到 Python 3。

9. **目前**：Python 在大模型（GPT-3、GPT-4、BERT等）、计算机视觉、智能推荐、自动驾驶、语音识别、数据科学、量化交易、自动化测试、自动化运维等领域都得到了广泛的应用。

### 1.3 Python的优缺点

#### 优点

1. **简单优雅**，跟其他很多编程语言相比，Python **更容易上手**。
2. 能用更少的代码做更多的事情，**提升开发效率**。
3. 开放源代码，拥有**强大的社区和生态圈**。
4. **能够做的事情非常多**，有极强的适应性。
5. **胶水语言**，能够黏合其他语言开发的东西。
6. 解释型语言，更容易**跨平台**，能够在多种操作系统上运行。

#### 缺点

Python 最主要的缺点是**执行效率低**（解释型语言的通病），如果更看重代码的执行效率，C、C++ 或 Go 可能是更好的选择。

## 2. 安装Python环境

### 2.1 下载Python

从官方网站的[下载页面](https://www.python.org/downloads/)找到下载链接，根据自己的操作系统选择合适的 Python 3安装程序。

### 2.2 Windows环境安装

1. 双击运行从官网下载的安装程序
2. **重要**：勾选"Add python.exe to PATH"选项，它会帮助我们将 Python 解释器添加到 Windows 系统的 PATH 环境变量中
3. 选择"Customize Installation"（自定义安装）
4. 在"Optional Features"中全选（特别是pip，Python的包管理工具）
5. 在"Advanced Options"中勾选：
   - "Add Python to environment variables"
   - "Precompile standard library"
6. 设置自定义安装路径（路径中不应包含中文、空格或其他特殊字符）
7. 点击"Install"开始安装

#### 验证安装

打开 Windows 的"命令行提示符"或 PowerShell，输入以下命令：

```bash
python --version
# 或
python -V
```

检查pip是否可用：

```bash
pip --version
# 或
pip -V
```

### 2.3 macOS环境安装

1. 从官网下载`.pkg`安装包
2. 双击运行，不断点击"继续"即可完成安装

#### 验证安装

在 macOS 的"终端"工具中输入：

```bash
python3 --version
pip3 --version
```

**注意**：macOS 系统中命令是`python3`和`pip3`，不是`python`和`pip`。

### 2.4 Linux环境安装

大多数 Linux 发行版都预装了 Python，如果没有，可以使用包管理器安装：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# 验证
python3 --version
pip3 --version
```

### 2.5 其他安装方式

#### Anaconda（不推荐）

Anaconda 会安装 Python 解释器以及一些常用的三方库，还提供了一些便捷的工具。**不推荐**的原因：
- 会安装一大堆有用没用的三方库（占用比较多的硬盘空间）
- 终端或命令提示符会被 Anaconda 篡改（每次启动自动激活虚拟环境）
- 不符合软件设计的**最小惊讶原则**

如果非要使用，推荐安装 **Miniconda**，它更轻量级。

#### PyCharm（IDE工具）

PyCharm 只是一个辅助写 Python 代码的工具，它本身并不具备运行 Python 代码的能力，运行 Python 代码靠的是 Python 解释器。有些 PyCharm 版本在创建 Python 项目时，如果检测不到你电脑上的 Python 环境，也会提示你联网下载 Python 解释器。

## 3. Python版本说明

### 3.1 版本号格式

大多数软件的版本号一般分为三段，形如A.B.C：
- **A**：大版本号，当软件整体重写升级或出现不向后兼容的改变时，才会增加A
- **B**：功能更新，出现新功能时增加B
- **C**：小的改动（例如：修复了某个Bug），只要有修改就增加C

### 3.2 Python 2 vs Python 3

- **Python 2**：已于2020年1月停止维护，不再推荐使用
- **Python 3**：当前主流版本，推荐使用

## 4. 第一个Python程序

### 4.1 交互式环境

安装完成后，可以在命令行中输入`python`（Windows）或`python3`（macOS/Linux）进入交互式环境：

```python
>>> print("Hello, World!")
Hello, World!
>>> 1 + 1
2
```

### 4.2 编写Python文件

创建一个名为`hello.py`的文件：

```python
print("Hello, World!")
```

运行文件：

```bash
python hello.py
# 或
python3 hello.py
```

## 5. 开发工具推荐

### 5.1 代码编辑器

- **VS Code**：轻量级，插件丰富
- **PyCharm**：专业Python IDE，功能强大
- **Sublime Text**：轻量级编辑器
- **Vim/Neovim**：命令行编辑器

### 5.2 包管理工具

- **pip**：Python官方包管理工具
- **conda**：Anaconda的包管理工具
- **poetry**：现代Python依赖管理工具

## 6. 总结

1. Python 语言很强大，可以做很多的事情，值得学习
2. 要使用 Python语言，首先得安装 Python 环境，也就是运行 Python 程序所需的 Python 解释器
3. Windows 系统使用`python --version`检查安装；macOS/Linux 系统使用`python3 --version`检查
4. 推荐使用 Python 3，Python 2 已停止维护
5. 选择合适的开发工具可以提高开发效率

