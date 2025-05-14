# 定义输出参数类
class OutputParameter:
    result: str = None
    status: bool = True
    data_list: list = []

# 主函数，系统会自动提取并使用这些参数
def main(name: str = "用户", age: int = 30, interests: list = None, is_active: bool = True):
    """
    示例脚本：处理用户信息并返回格式化结果
    
    :param name: 用户名
    :param age: 用户年龄
    :param interests: 用户兴趣爱好列表
    :param is_active: 是否活跃用户
    :return: 包含处理结果的字典
    """
    # 参数处理
    if interests is None:
        interests = ["编程", "阅读"]
    
    # 业务逻辑
    greeting = f"你好，{name}！"
    age_info = f"你今年{age}岁。"
    status = "活跃" if is_active else "非活跃"
    
    # 处理兴趣列表
    interests_text = "、".join(interests)
    
    # 构建返回结果
    result = {
        "status": True,
        "message": "处理成功",
        "result": {
            "greeting": greeting,
            "age_info": age_info,
            "user_status": status,
            "interests": interests,
            "interests_text": f"你的兴趣包括：{interests_text}",
            "summary": f"{greeting} {age_info} 你是一位{status}用户，兴趣有{interests_text}。"
        }
    }
    
    return result
