#!/usr/bin/env python3
"""
빠른 API 테스트
"""

import requests
import json
from datetime import datetime

SERVER_URL = "http://localhost:8000"

def test_simple_detection():
    """가장 간단한 형태의 탐지 결과 테스트"""
    
    data = {
        "cctv_id": "camera_01",
        "bbox": [100, 100, 200, 200],
        "pos": [150, 150],
        "risk": "red",
        "captured_at": datetime.now().isoformat(),
        "frame_url": "/frames/test.jpg",
        "bird_count": 1
    }
    
    print("📤 전송할 데이터:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{SERVER_URL}/detect",
            json=data,
            timeout=10
        )
        
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📝 응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ 성공!")
                return True
            else:
                print(f"❌ 서버 에러: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP 에러: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return False

def test_ping():
    """서버 핑 테스트"""
    try:
        response = requests.get(f"{SERVER_URL}/ping", timeout=5)
        print(f"🏓 Ping 응답: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Ping 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔬 빠른 API 테스트")
    print("=" * 50)
    
    # 서버 핑 테스트
    if test_ping():
        print()
        # 탐지 결과 테스트
        test_simple_detection()
    else:
        print("❌ 서버에 연결할 수 없습니다.")
