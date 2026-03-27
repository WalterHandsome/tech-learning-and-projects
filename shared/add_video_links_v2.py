#!/usr/bin/env python3
"""批量为学习笔记文档补充多平台视频链接（B站、慕课网、Coursera等）

在已有的 YouTube 视频推荐基础上，追加中文平台和其他国际平台的优质资源。
"""

from pathlib import Path

# 补充的多平台视频资源
EXTRA_VIDEO_MAP = {
    # ==================== AI Agent ====================
    "ai-agent/00-基础概念/AI Agent概述与发展": """
### 📺 B站（Bilibili）
- [李沐 - 动手学深度学习](https://www.bilibili.com/video/BV1if4y147hS) — 亚马逊首席科学家，中文AI教育天花板
- [跟李沐学AI - GPT/Transformer论文精读](https://space.bilibili.com/1567748478) — 论文精读系列，深入理解大模型

### 🎓 Coursera / edX
- [Andrew Ng - AI For Everyone](https://www.coursera.org/learn/ai-for-everyone) — 非技术角度理解AI（免费旁听）
""",
    "ai-agent/00-基础概念/大语言模型基础": """
### 📺 B站（Bilibili）
- [李沐 - Transformer论文逐段精读](https://www.bilibili.com/video/BV1pu411o7BE) — Attention Is All You Need 论文精读
- [李沐 - GPT/GPT-2/GPT-3论文精读](https://www.bilibili.com/video/BV1AF411b7xQ) — GPT系列论文精读
- [3Blue1Brown中文 - 神经网络系列](https://www.bilibili.com/video/BV1bx411M7Zx) — 神经网络可视化（中文字幕）

### 🎓 Coursera
- [DeepLearning.AI - Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning) — 吴恩达深度学习专项（免费旁听）
""",
    "ai-agent/00-基础概念/Prompt Engineering": """
### 📺 B站（Bilibili）
- [吴恩达 - Prompt Engineering中文字幕](https://www.bilibili.com/video/BV1No4y1t7Zn) — DeepLearning.AI课程中文版

### 🌐 其他平台
- [Learn Prompting](https://learnprompting.org/zh-Hans/docs/intro) — 免费开源Prompt工程教程（中文版）
""",
    "ai-agent/02-Agent框架/LangGraph工作流编排": """
### 📺 B站（Bilibili）
- [LangChain官方 - LangGraph教程中文字幕](https://www.bilibili.com/video/BV1dH4y1P7FY) — LangGraph入门到实战

### 🎓 DeepLearning.AI（免费）
- [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — 吴恩达+LangChain联合出品
""",
    "ai-agent/02-Agent框架/CrewAI多Agent协作": """
### 📺 B站（Bilibili）
- [CrewAI多Agent实战教程](https://www.bilibili.com/video/BV1Bm421N7BH) — CrewAI中文实战

### 🎓 DeepLearning.AI（免费）
- [Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent系统实战
""",
    "ai-agent/03-RAG进阶/RAG架构与核心流程": """
### 📺 B站（Bilibili）
- [RAG从入门到精通](https://www.bilibili.com/video/BV1PD421E7mN) — RAG完整中文教程
- [李沐 - 检索增强生成论文精读](https://space.bilibili.com/1567748478) — RAG论文精读

### 🎓 DeepLearning.AI（免费）
- [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) — 高级RAG构建
""",
    "ai-agent/15-Agentic设计模式/Anthropic Agent设计模式": """
### 📺 B站（Bilibili）
- [吴恩达 - Agentic AI设计模式中文字幕](https://www.bilibili.com/video/BV1Bz421B7bG) — Agentic设计模式讲解

### 🎓 DeepLearning.AI（免费）
- [Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI完整课程
""",
    # ==================== Python ====================
    "python/00-Python基础/Python简介与安装": """
### 📺 B站（Bilibili）
- [黑马程序员 - Python从入门到精通](https://www.bilibili.com/video/BV1qW4y1a7fU) — 600万播放，中文Python入门首选
- [小甲鱼 - Python零基础入门](https://www.bilibili.com/video/BV1c4411e77t) — 经典Python入门系列

### 🌐 其他平台
- [廖雪峰Python教程](https://www.liaoxuefeng.com/wiki/1016959663602400) — 中文最经典的Python在线教程
- [Python官方教程中文版](https://docs.python.org/zh-cn/3/tutorial/) — 官方教程
""",
    "python/00-Python基础/Python面向对象编程": """
### 📺 B站（Bilibili）
- [黑马程序员 - Python面向对象](https://www.bilibili.com/video/BV1qW4y1a7fU) — 包含OOP完整章节
- [小甲鱼 - Python面向对象](https://www.bilibili.com/video/BV1c4411e77t) — OOP部分讲解清晰

### 🌐 其他平台
- [廖雪峰 - 面向对象编程](https://www.liaoxuefeng.com/wiki/1016959663602400/1017495723838528) — 中文OOP教程
""",
    "python/01-Web开发/FastAPI快速入门": """
### 📺 B站（Bilibili）
- [FastAPI中文教程](https://www.bilibili.com/video/BV1iN411X72b) — FastAPI完整中文教程

### 🌐 其他平台
- [FastAPI官方中文文档](https://fastapi.tiangolo.com/zh/) — 官方中文文档（含交互式教程）
""",
    "python/01-Web开发/Django基础": """
### 📺 B站（Bilibili）
- [黑马程序员 - Django教程](https://www.bilibili.com/video/BV1vK4y1o7jH) — Django完整中文教程
- [刘江的Django教程](https://www.bilibili.com/video/BV1pE411q7Nj) — Django实战教程

### 🌐 其他平台
- [Django官方中文文档](https://docs.djangoproject.com/zh-hans/) — 官方中文文档
""",
    "python/02-数据分析/Pandas应用": """
### 📺 B站（Bilibili）
- [莫烦Python - Pandas教程](https://www.bilibili.com/video/BV1Ex411L7oT) — Pandas快速入门
- [黑马程序员 - 数据分析](https://www.bilibili.com/video/BV1hx411d7jb) — 包含Pandas完整教程

### 🌐 其他平台
- [Pandas官方中文文档](https://www.pypandas.cn/) — 中文API文档
""",
    "python/03-机器学习/浅谈机器学习": """
### 📺 B站（Bilibili）
- [李沐 - 动手学深度学习](https://www.bilibili.com/video/BV1if4y147hS) — 中文AI教育天花板，500+所大学采用
- [吴恩达 - 机器学习中文字幕](https://www.bilibili.com/video/BV1Pa411X76s) — 经典ML课程中文版
- [StatQuest中文字幕](https://www.bilibili.com/video/BV1R4411V7Bk) — 机器学习概念可视化

### 🎓 Coursera
- [Machine Learning Specialization](https://www.coursera.org/specializations/machine-learning-introduction) — 吴恩达2022新版（免费旁听）

### 📖 在线教材
- [动手学深度学习](https://zh.d2l.ai/) — 李沐团队，可运行的中文深度学习教材
""",
    "python/03-机器学习/深度学习框架应用": """
### 📺 B站（Bilibili）
- [李沐 - 动手学深度学习 PyTorch版](https://www.bilibili.com/video/BV1if4y147hS) — PyTorch实战
- [刘二大人 - PyTorch深度学习实践](https://www.bilibili.com/video/BV1Y7411d7Ys) — PyTorch经典入门

### 📖 在线教材
- [动手学深度学习](https://zh.d2l.ai/) — 含PyTorch/TensorFlow代码
""",
    # ==================== Java ====================
    "java/00-Java基础/JVM内存模型与垃圾回收": """
### 📺 B站（Bilibili）
- [尚硅谷 - JVM完整教程](https://www.bilibili.com/video/BV1PJ411n7xZ) — 宋红康JVM深入讲解，中文JVM教程首选
- [黑马程序员 - JVM虚拟机](https://www.bilibili.com/video/BV1yE411Z7AP) — JVM系统教程
""",
    "java/00-Java基础/Java并发编程": """
### 📺 B站（Bilibili）
- [黑马程序员 - Java并发编程](https://www.bilibili.com/video/BV16J411h7Rd) — Java并发完整教程
- [尚硅谷 - JUC并发编程](https://www.bilibili.com/video/BV1Kw411Z7dF) — JUC深入讲解
""",
    "java/01-框架/Spring基础01": """
### 📺 B站（Bilibili）
- [尚硅谷 - Spring6完整教程](https://www.bilibili.com/video/BV1kR4y1b7Qc) — Spring最新版完整教程
- [黑马程序员 - SSM框架](https://www.bilibili.com/video/BV1Fi4y1S7ix) — Spring+SpringMVC+MyBatis

### 🌐 其他平台
- [Spring官方文档](https://spring.io/guides) — 官方入门指南
- [Baeldung](https://www.baeldung.com/) — Java/Spring最权威的英文教程网站
""",
    "java/01-框架/SpringBoot基础": """
### 📺 B站（Bilibili）
- [尚硅谷 - SpringBoot3完整教程](https://www.bilibili.com/video/BV1Es4y1q7Bf) — SpringBoot3最新教程
- [黑马程序员 - SpringBoot实战](https://www.bilibili.com/video/BV1Lq4y1J77x) — SpringBoot项目实战

### 🌐 其他平台
- [Baeldung - Spring Boot](https://www.baeldung.com/spring-boot) — 英文Spring Boot权威教程
""",
    "java/01-框架/SpringCloud01": """
### 📺 B站（Bilibili）
- [尚硅谷 - SpringCloud完整教程](https://www.bilibili.com/video/BV1LQ4y127n4) — 微服务全家桶
- [黑马程序员 - 微服务实战](https://www.bilibili.com/video/BV1LQ4y127n4) — 微服务项目实战
""",
    "java/02-中间件/Redis分布式缓存": """
### 📺 B站（Bilibili）
- [黑马程序员 - Redis实战](https://www.bilibili.com/video/BV1cr4y1671t) — Redis完整中文教程
- [尚硅谷 - Redis7教程](https://www.bilibili.com/video/BV1Fd4y1S7dz) — Redis7最新教程
""",
    "java/02-中间件/RabbitMQ": """
### 📺 B站（Bilibili）
- [黑马程序员 - RabbitMQ教程](https://www.bilibili.com/video/BV1mN4y1Z7t9) — RabbitMQ完整中文教程
- [尚硅谷 - RabbitMQ教程](https://www.bilibili.com/video/BV1cb4y1o7zz) — RabbitMQ深入讲解
""",
    "java/02-中间件/Elasticsearch基础": """
### 📺 B站（Bilibili）
- [黑马程序员 - Elasticsearch教程](https://www.bilibili.com/video/BV1LQ4y127n4) — ES完整中文教程
- [尚硅谷 - Elasticsearch教程](https://www.bilibili.com/video/BV1hh411D7sb) — ES深入讲解
""",
    "java/03-容器化/Docker实用篇": """
### 📺 B站（Bilibili）
- [黑马程序员 - Docker实战](https://www.bilibili.com/video/BV1HP4118797) — Docker完整中文教程
- [尚硅谷 - Docker教程](https://www.bilibili.com/video/BV1gr4y1U7CY) — Docker深入讲解
""",
    "java/03-容器化/Kubernetes第1天": """
### 📺 B站（Bilibili）
- [黑马程序员 - Kubernetes教程](https://www.bilibili.com/video/BV1Qv41167ck) — K8s完整中文教程
- [尚硅谷 - Kubernetes教程](https://www.bilibili.com/video/BV1GT4y1A756) — K8s深入讲解
""",
    "java/07-数据库/MySQL基础": """
### 📺 B站（Bilibili）
- [黑马程序员 - MySQL教程](https://www.bilibili.com/video/BV1Kr4y1i7ru) — MySQL完整中文教程（最受欢迎）
- [尚硅谷 - MySQL高级](https://www.bilibili.com/video/BV1iq4y1u7vj) — MySQL高级特性
""",
    # ==================== Frontend ====================
    "frontend/01-JavaScript基础/ES6+新特性": """
### 📺 B站（Bilibili）
- [尚硅谷 - ES6-ES13新特性](https://www.bilibili.com/video/BV1uK411H7on) — ES6+完整中文教程
- [黑马程序员 - JavaScript高级](https://www.bilibili.com/video/BV1Y84y1L7Nn) — JS高级特性

### 🌐 其他平台
- [现代JavaScript教程](https://zh.javascript.info/) — 最全面的中文JS教程（免费在线）
- [MDN Web Docs中文](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript) — Mozilla官方中文文档
""",
    "frontend/03-React/React基础与JSX": """
### 📺 B站（Bilibili）
- [尚硅谷 - React18教程](https://www.bilibili.com/video/BV1ZB4y1Z7o8) — React18完整中文教程
- [黑马程序员 - React教程](https://www.bilibili.com/video/BV1Z44y1K7Fj) — React项目实战

### 🌐 其他平台
- [React官方中文文档](https://zh-hans.react.dev/) — 官方中文文档（2023新版）
""",
    "frontend/04-Vue/Vue3基础与组合式API": """
### 📺 B站（Bilibili）
- [尚硅谷 - Vue3完整教程](https://www.bilibili.com/video/BV1Za4y1r7KE) — Vue3完整中文教程
- [黑马程序员 - Vue3教程](https://www.bilibili.com/video/BV1HV4y1a7n4) — Vue3项目实战
- [coderwhy - Vue3+TS](https://www.bilibili.com/video/BV1WP4y187Tu) — Vue3+TypeScript深入

### 🌐 其他平台
- [Vue3官方中文文档](https://cn.vuejs.org/) — 官方中文文档
""",
    "frontend/02-TypeScript/TypeScript基础入门": """
### 📺 B站（Bilibili）
- [黑马程序员 - TypeScript教程](https://www.bilibili.com/video/BV1YP411S7cC) — TS完整中文教程
- [尚硅谷 - TypeScript教程](https://www.bilibili.com/video/BV1Xy4y1v7S2) — TS深入讲解

### 🌐 其他平台
- [TypeScript官方中文文档](https://www.typescriptlang.org/zh/) — 官方中文文档
""",
    "frontend/07-Node.js/Node.js基础与模块系统": """
### 📺 B站（Bilibili）
- [黑马程序员 - Node.js教程](https://www.bilibili.com/video/BV1a34y167AZ) — Node.js完整中文教程
- [尚硅谷 - Node.js教程](https://www.bilibili.com/video/BV1gM411W7ex) — Node.js深入讲解
""",
    "frontend/00-HTML与CSS基础/Flex与Grid布局": """
### 📺 B站（Bilibili）
- [黑马程序员 - CSS布局教程](https://www.bilibili.com/video/BV1p84y1P7Z5) — Flex/Grid完整教程

### 🌐 其他平台
- [Flexbox Froggy](https://flexboxfroggy.com/#zh-cn) — Flexbox游戏化学习（中文）
- [Grid Garden](https://cssgridgarden.com/#zh-cn) — CSS Grid游戏化学习（中文）
""",
    # ==================== iOS ====================
    "ios/01-SwiftUI/SwiftUI基础与布局": """
### 📺 B站（Bilibili）
- [SwiftUI中文教程](https://www.bilibili.com/video/BV1s3411g7ab) — SwiftUI入门到实战

### 🎓 斯坦福公开课
- [Stanford CS193p - SwiftUI](https://cs193p.sites.stanford.edu/) — 斯坦福iOS开发课程（免费，B站有中文字幕版）

### 🌐 其他平台
- [Hacking with Swift - 100 Days of SwiftUI](https://www.hackingwithswift.com/100/swiftui) — 最受欢迎的SwiftUI学习路径
""",
    # ==================== Android ====================
    "android/01-Jetpack Compose/Compose基础与布局": """
### 📺 B站（Bilibili）
- [Jetpack Compose中文教程](https://www.bilibili.com/video/BV1HV4y1a7n4) — Compose入门到实战

### 🌐 其他平台
- [Android官方Compose教程](https://developer.android.com/courses/android-basics-compose/course) — Google官方Compose课程（免费）
- [Jetpack Compose官方文档](https://developer.android.com/develop/ui/compose/documentation) — 官方文档
""",
    "android/00-Kotlin基础/Kotlin语法基础": """
### 📺 B站（Bilibili）
- [黑马程序员 - Kotlin教程](https://www.bilibili.com/video/BV1wf4y1s7TG) — Kotlin完整中文教程

### 🌐 其他平台
- [Kotlin官方中文文档](https://book.kotlincn.net/) — 官方中文文档
- [Kotlin Koans](https://play.kotlinlang.org/koans/) — 官方交互式练习
""",
}


VIDEO_MARKER = "## 🎬 推荐视频资源"
EXTRA_MARKER = "### 📺 B站"


def find_matching_file(base_dir: Path, key: str) -> Path | None:
    parts = key.split("/")
    search_dir = base_dir
    for part in parts[:-1]:
        search_dir = search_dir / part
    filename = parts[-1]
    candidate = search_dir / f"{filename}.md"
    if candidate.exists():
        return candidate
    if search_dir.exists():
        for f in search_dir.iterdir():
            if f.suffix == ".md" and filename in f.stem:
                return f
    return None


def append_extra_videos(filepath: Path, extra_block: str) -> bool:
    content = filepath.read_text(encoding="utf-8")
    # 已经有B站链接了，跳过
    if EXTRA_MARKER in content:
        return False
    # 在文件末尾追加
    updated = content.rstrip() + "\n" + extra_block.strip() + "\n"
    filepath.write_text(updated, encoding="utf-8")
    return True


def main():
    base_dir = Path(__file__).resolve().parent.parent / "learning-notes"
    added, skipped, not_found = 0, 0, 0

    for key, extra_block in EXTRA_VIDEO_MAP.items():
        filepath = find_matching_file(base_dir, key)
        if filepath is None:
            print(f"  ❌ 未找到: {key}")
            not_found += 1
            continue
        if append_extra_videos(filepath, extra_block):
            print(f"  ✅ {filepath.relative_to(base_dir)}")
            added += 1
        else:
            skipped += 1

    print(f"\n完成: {added} 个文件已补充多平台视频, {skipped} 个已有跳过, {not_found} 个未找到")


if __name__ == "__main__":
    main()
