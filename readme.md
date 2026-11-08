# Supplier Agent：客商准入评分 API

## 项目简介
这个项目解决让大模型自己给不同公司打分的问题

## 功能
- `POST /score`：这个是自己定义，写的函数来做的的python函数打分
- `POST /score_ai`：让大模型回复这个打分

## 设计思路
- 为什么让大模型只判断经营范围，而分数由代码计算？
 因为大模型做分数计算可能出错，而数据计算这种问题可以靠代码进行解决。
- 怎么保证大模型输出的格式正确？
规定一个schema，并且之后进行检验
- Gemini 不可用时怎么处理？
让程序自动换一个模型，换到可用为止，不可用就报错

## 技术栈
Python、FastAPI、Pydantic、Google Gemini API

## 如何运行
1. 创建虚拟环境并安装依赖
2. 在项目根目录新建 `.env`，写入 `GEMINI_API_KEY=你的key`
3. 运行 `uvicorn main:app --reload`
4. 打开 http://127.0.0.1:8000/docs 测试