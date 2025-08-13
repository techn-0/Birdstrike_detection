"""
간단한 조류 탐지 결과 전송 테스트
외부 AI 모델에서 사용할 수 있는 최소한의 예제
"""

import requests
import json
from datetime import datetime
import random

# 서버 URL 설정
SERVER_URL = "http://localhost:8000"

def send_bird_detection(cctv_id: str, bbox: list, confidence: float):
    """
    조류 탐지 결과를 서버로 전송하는 간단한 함수
    
    Args:
        cctv_id: 카메라 ID (예: "camera_01")
        bbox: 바운딩 박스 [x1, y1, x2, y2]
        confidence: 신뢰도 (0.0 ~ 1.0)
    
    Returns:
        bool: 전송 성공 여부
    """
    
    # 전송할 데이터 구성
    data = {
        "cctv_id": cctv_id,
        "bbox": bbox,
        "confidence": confidence,
        "captured_at": datetime.now().isoformat(),
        "bird_count": 1
    }
    
    try:
        # API 요청 전송
        response = requests.post(
            f"{SERVER_URL}/detect/result",
            json=data,
            timeout=10
        )
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ 탐지 결과 전송 성공: {cctv_id}")
                return True
            else:
                print(f"❌ 서버 에러: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP 에러 {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 전송 실패: {e}")
        return False

def test_basic_detection():
    """기본 탐지 테스트"""
    print("🔍 기본 조류 탐지 테스트 시작...")
    
    # 테스트 데이터
    test_cases = [
        {
            "cctv_id": "camera_01",
            "bbox": [100.5, 150.2, 120.3, 165.8],  # 작은 새
            "confidence": 0.75
        },
        {
            "cctv_id": "runway_01", 
            "bbox": [300.1, 200.5, 350.7, 240.2],  # 중간 크기 새
            "confidence": 0.85
        },
        {
            "cctv_id": "camera_02",
            "bbox": [450.2, 100.8, 500.9, 160.3],  # 큰 새
            "confidence": 0.92
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}/3] 테스트 케이스 {i} 전송 중...")
        print(f"  카메라: {case['cctv_id']}")
        print(f"  바운딩박스: {case['bbox']}")
        print(f"  신뢰도: {case['confidence']}")
        
        if send_bird_detection(**case):
            success_count += 1
    
    print(f"\n📊 테스트 완료: {success_count}/3 성공")

def simulate_real_model_output():
    """실제 AI 모델 출력을 시뮬레이션"""
    print("\n🤖 AI 모델 출력 시뮬레이션...")
    
    # 실제 모델에서 나올 수 있는 결과들을 시뮬레이션
    cameras = ["camera_01", "camera_02", "runway_01", "runway_02"]
    
    for _ in range(5):
        # 랜덤한 탐지 결과 생성
        camera = random.choice(cameras)
        
        # 바운딩 박스 생성 (실제와 유사한 범위)
        x1 = random.uniform(50, 400)
        y1 = random.uniform(50, 300)
        x2 = x1 + random.uniform(10, 100)
        y2 = y1 + random.uniform(8, 80)
        bbox = [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
        
        # 신뢰도 생성
        confidence = random.uniform(0.3, 0.95)
        
        print(f"\n🔍 {camera} 탐지: 신뢰도 {confidence:.3f}")
        send_bird_detection(camera, bbox, confidence)

def check_server():
    """서버 연결 확인"""
    try:
        response = requests.get(f"{SERVER_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 연결 성공")
            return True
        else:
            print(f"⚠️ 서버 응답 이상: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("💡 백엔드 서버가 실행되고 있는지 확인해주세요.")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚁 조류 탐지 시스템 - 간단 테스트")
    print("=" * 50)
    
    # 서버 연결 확인
    if not check_server():
        exit(1)
    
    # 기본 테스트 실행
    test_basic_detection()
    
    # 시뮬레이션 테스트
    simulate_real_model_output()
    
    print("\n🎉 모든 테스트 완료!")
