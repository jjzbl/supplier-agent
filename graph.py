from typing import TypedDict
from main import judge_scope,get_risk_level
from fastapi import HTTPException
from langgraph.graph import StateGraph, START, END
    

class SupplierState(TypedDict):
    name: str                   # 公司名称
    years_established: int      # 成立年限
    registered_capital: float   # 注册资本（万元）
    business_scope: str         # 经营范围
    rule_score: int             # 分数1
    llm_score: int              # 分数2
    llm_success: bool           # llm是否成功
    total_score: int            # 总分
    risk_level: str             #风险等级

#节点函数
def rule_score_node(state: SupplierState) -> dict:
    years_established = state["years_established"]
    registered_capital = state["registered_capital"]
    score = 0
    if years_established >=5:
        score +=50     
    else:
        score += 20      
    
    if registered_capital >= 1000:
        score += 50        
    else:
        score += 20        

    return {"rule_score": score}

def llm_score_node(state: SupplierState) -> dict:
    try:
        judgment = judge_scope(state["business_scope"])
        judgment_score = {"高度相关": 30, "部分相关": 15, "无关": 0}[judgment.relevance]
        return {"llm_score": judgment_score, "llm_success": True}
    except HTTPException:
        return {"llm_success":False}

def fallback_node(state: SupplierState) -> dict:
    return {"llm_score": 0}

def aggregate_node(state: SupplierState) -> dict:
    total_score = state["llm_score"] +state["rule_score"]

    risk_level = get_risk_level(total_score)
    
    return {"total_score": total_score, "risk_level": risk_level}

def human_review_node(state: SupplierState) -> dict:
    print("需要人工复核")
    return {}

#路由函数

def route_after_llm(state: SupplierState) -> str:
    if state["llm_success"]:
       return "aggregate"
    else:
       return "fallback"

def route_after_aggregate(state: SupplierState) -> str:
    if state["risk_level"] == "高风险":
        return "human_review"
    else:
        return END

builder = StateGraph(SupplierState)

builder.add_node("rule_check", rule_score_node)
builder.add_node("llm_judge", llm_score_node)
builder.add_node("fallback", fallback_node)
builder.add_node("aggregate", aggregate_node)
builder.add_node("human_review", human_review_node)

builder.add_edge(START, "rule_check")
builder.add_edge("rule_check", "llm_judge")
builder.add_conditional_edges("llm_judge", route_after_llm)
builder.add_edge("fallback", "aggregate")
builder.add_conditional_edges("aggregate", route_after_aggregate)
builder.add_edge("human_review", END)

graph = builder.compile()

result = graph.invoke({
    "name": "测试化工有限公司",
    "years_established":2,
    "registered_capital": 100,
    "business_scope": "奶茶店",
})
print(result)
