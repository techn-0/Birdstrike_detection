# 예시: JSON 파일로 데이터 영속화
import json
import os
from datetime import datetime

USER_DATA_FILE = "/data/users.json"

def save_users_to_file(users_data):
    """사용자 데이터를 파일에 저장"""
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    
    # datetime 객체를 문자열로 변환
    serializable_data = {}
    for username, user_data in users_data.items():
        user_copy = user_data.copy()
        if isinstance(user_copy.get('created_at'), datetime):
            user_copy['created_at'] = user_copy['created_at'].isoformat()
        serializable_data[username] = user_copy
    
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, ensure_ascii=False, indent=2)

def load_users_from_file():
    """파일에서 사용자 데이터 로드"""
    if not os.path.exists(USER_DATA_FILE):
        return {}
    
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 문자열을 datetime 객체로 변환
        for username, user_data in data.items():
            if 'created_at' in user_data:
                user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
        
        return data
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}
