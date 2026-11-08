# Supplier Agent：客商准入评分 API

## 项目简介
贸易公司在引入新的供应商（客商）时，需要先评估它的风险。
这个项目提供一个 API：输入公司的成立年限、注册资本和经营范围，返回评分、风险等级和每一项的评分理由。

## 功能
- `POST /score`：纯规则打分，只用成立年限和注册资本，作为对照版本。
- `POST /score_ai`：规则 + 大模型。成立年限、注册资本由代码按规则计算；经营范围由大模型判断与化工贸易的相关程度，再由代码换算成分数。

## 设计思路
**1. 大模型只做判断，分数由代码计算**
最初的版本让大模型按规则直接打总分，测试时发现它把 40 + 30 + 0 算成了 75。
数值计算用代码可以保证完全准确，所以只把"理解经营范围"这种需要语言理解的部分交给大模型。

**2. 保证大模型输出的格式正确**
- 用 `response_schema` 要求 Gemini 按规定的结构返回 JSON；
- 用 Pydantic 的 `model_validate_json` 再次校验，相关程度用 `Literal` 限定为"高度相关 / 部分相关 / 无关"三个值之一。
大模型的输出被当作外部输入，使用前必须校验。

**3. Gemini 不可用时的处理**
准备了一个备用模型列表，某个模型调用失败（如 503 繁忙）或返回格式不合法时，自动换下一个模型重试；
全部失败时，返回 503 和明确的错误提示，而不是笼统的 500。

## 技术栈
Python、FastAPI、Pydantic、Google Gemini API

## 如何运行
1. 创建虚拟环境并安装依赖：
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
2. 在项目根目录新建 `.env`，写入 `GEMINI_API_KEY=你的key`
3. 运行 `uvicorn main:app --reload`
4. 打开 http://127.0.0.1:8000/docs 测试