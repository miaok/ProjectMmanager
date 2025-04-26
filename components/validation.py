import re

def validate_id_card(id_card):
    """
    验证中国身份证号码
    支持15位和18位身份证号
    18位身份证号末位校验码验证
    
    返回: (bool, str) - (是否有效, 错误信息)
    """
    if not id_card:
        return False, "身份证号不能为空"
    
    # 移除所有空格
    id_card = id_card.strip()
    
    # 15位身份证号码验证
    if len(id_card) == 15:
        # 15位身份证号全部为数字
        if not re.match(r'^\d{15}$', id_card):
            return False, "15位身份证号应全部为数字"
        
        # 验证出生日期
        try:
            year = int('19' + id_card[6:8])
            month = int(id_card[8:10])
            day = int(id_card[10:12])
            
            # 简单的日期验证
            if month < 1 or month > 12:
                return False, "身份证号中的月份无效"
            if day < 1 or day > 31:
                return False, "身份证号中的日期无效"
                
            return True, ""
        except:
            return False, "身份证号中的出生日期无效"
    
    # 18位身份证号码验证
    elif len(id_card) == 18:
        # 前17位全部为数字，最后一位可能是数字或X
        if not re.match(r'^\d{17}[\dXx]$', id_card):
            return False, "18位身份证号前17位应为数字，最后一位可以是数字或X"
        
        # 验证出生日期
        try:
            year = int(id_card[6:10])
            month = int(id_card[10:12])
            day = int(id_card[12:14])
            
            # 简单的日期验证
            if year < 1900 or year > 2100:
                return False, "身份证号中的年份无效"
            if month < 1 or month > 12:
                return False, "身份证号中的月份无效"
            if day < 1 or day > 31:
                return False, "身份证号中的日期无效"
            
            # 校验码验证
            factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            checksum_map = '10X98765432'
            
            # 计算校验和
            checksum = 0
            for i in range(17):
                checksum += int(id_card[i]) * factors[i]
            
            # 计算校验码
            check_digit = checksum_map[checksum % 11]
            
            # 验证校验码
            if check_digit != id_card[17].upper():
                return False, "身份证号校验码错误"
                
            return True, ""
        except:
            return False, "身份证号中的出生日期无效"
    
    else:
        return False, "身份证号长度应为15位或18位"

def validate_phone(phone):
    """
    验证中国手机号码
    支持11位手机号，以1开头
    
    返回: (bool, str) - (是否有效, 错误信息)
    """
    if not phone:
        return True, ""  # 手机号可以为空
    
    # 移除所有空格和连字符
    phone = re.sub(r'[\s-]', '', phone)
    
    # 验证手机号格式
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False, "手机号格式不正确，应为11位数字且以1开头"
    
    return True, ""
