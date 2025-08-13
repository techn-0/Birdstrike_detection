"""
외부 모델 프로젝트에서 탐지 결과를 전송하는 테스트 스크립트
실제 AI 모델의 예측 결과를 시뮬레이션합니다.
"""

import requests
import json
import time
import random
import base64
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import cv2
import numpy as np

class BirdDetectionSimulator:
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        조류 탐지 시뮬레이터 초기화
        
        Args:
            server_url: 백엔드 서버 URL
        """
        self.server_url = server_url
        self.session = requests.Session()
        
        # 테스트용 카메라 ID들
        self.camera_ids = ["camera_01", "camera_02", "camera_03", "runway_01", "runway_02"]
        
        print(f"🚁 조류 탐지 시뮬레이터 초기화 완료")
        print(f"📡 서버 URL: {server_url}")
    
    def create_dummy_image(self, width: int = 640, height: int = 480) -> bytes:
        """테스트용 더미 이미지 생성"""
        # 파란 하늘 배경 생성
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:, :] = [135, 206, 235]  # 하늘색 배경
        
        # 랜덤 위치에 "새" 모양 점 그리기
        bird_x = random.randint(50, width-50)
        bird_y = random.randint(50, height-50)
        cv2.circle(img, (bird_x, bird_y), 3, (0, 0, 0), -1)  # 검은 점
        
        # 이미지를 JPEG로 인코딩
        _, encoded_img = cv2.imencode('.jpg', img)
        return encoded_img.tobytes()
    
    def generate_realistic_detection(self, camera_id: str) -> dict:
        """실제 탐지 결과와 유사한 데이터 생성"""
        
        # 실제 CSV 데이터 범위를 참고한 realistic한 값들
        scenarios = [
            # 작은 새 (멀리 있는 새)
            {
                "bbox_size": (5, 8, 15, 20),
                "confidence_range": (0.25, 0.35),
                "position": (100, 600, 100, 400)
            },
            # 중간 크기 새
            {
                "bbox_size": (15, 25, 30, 50),
                "confidence_range": (0.4, 0.7),
                "position": (200, 500, 150, 350)
            },
            # 큰 새 (가까이 있는 새)
            {
                "bbox_size": (30, 50, 80, 120),
                "confidence_range": (0.6, 0.9),
                "position": (150, 450, 100, 300)
            }
        ]
        
        scenario = random.choice(scenarios)
        
        # 바운딩 박스 생성 (x1, y1, x2, y2)
        x1 = random.randint(*scenario["position"][:2])
        y1 = random.randint(*scenario["position"][2:])
        width = random.randint(*scenario["bbox_size"][:2])
        height = random.randint(*scenario["bbox_size"][2:])
        x2 = x1 + width
        y2 = y1 + height
        
        # 신뢰도 생성
        confidence = random.uniform(*scenario["confidence_range"])
        
        # 더미 이미지 생성 및 base64 인코딩
        image_bytes = self.create_dummy_image()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        return {
            "cctv_id": camera_id,
            "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
            "confidence": round(confidence, 4),
            "captured_at": datetime.now().isoformat(),
            "image_name": f"{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            "image_data": image_b64,
            "bird_count": random.randint(1, 3)
        }
    
    def send_detection(self, detection_data: dict) -> bool:
        """탐지 결과를 서버로 전송"""
        try:
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return True
                else:
                    print(f"❌ 서버 에러: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP 에러 {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 요청 타임아웃")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ 서버 연결 실패")
            return False
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
            return False
    
    def test_single_detection(self, camera_id: str = None):
        """단일 탐지 결과 전송 테스트"""
        camera_id = camera_id or random.choice(self.camera_ids)
        
        print(f"\n🔍 단일 탐지 테스트 시작 - 카메라: {camera_id}")
        
        detection = self.generate_realistic_detection(camera_id)
        print(f"📊 생성된 탐지 데이터:")
        print(f"   - 바운딩 박스: {detection['bbox']}")
        print(f"   - 신뢰도: {detection['confidence']}")
        print(f"   - 새 개체 수: {detection['bird_count']}")
        
        success = self.send_detection(detection)
        
        if success:
            print(f"✅ 탐지 결과 전송 성공!")
        else:
            print(f"❌ 탐지 결과 전송 실패!")
        
        return success
    
    def test_multiple_detections(self, count: int = 5, interval: float = 2.0):
        """연속 탐지 결과 전송 테스트"""
        print(f"\n🔄 연속 탐지 테스트 시작 - {count}개 전송, {interval}초 간격")
        
        success_count = 0
        
        for i in range(count):
            camera_id = random.choice(self.camera_ids)
            detection = self.generate_realistic_detection(camera_id)
            
            print(f"\n[{i+1}/{count}] 📡 {camera_id} 탐지 결과 전송 중...")
            
            success = self.send_detection(detection)
            if success:
                success_count += 1
                print(f"✅ 성공 (신뢰도: {detection['confidence']:.3f})")
            else:
                print(f"❌ 실패")
            
            # 마지막이 아니면 대기
            if i < count - 1:
                time.sleep(interval)
        
        print(f"\n📊 연속 탐지 테스트 완료: {success_count}/{count} 성공")
        return success_count, count
    
    def test_high_risk_scenario(self):
        """고위험 시나리오 테스트 (높은 신뢰도)"""
        print(f"\n🚨 고위험 시나리오 테스트 시작")
        
        # 활주로 근처 카메라에서 높은 신뢰도 탐지
        detection = {
            "cctv_id": "runway_01",
            "bbox": [300.5, 200.3, 380.7, 250.8],  # 큰 바운딩 박스
            "confidence": 0.92,  # 높은 신뢰도
            "captured_at": datetime.now().isoformat(),
            "image_name": f"high_risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            "image_data": base64.b64encode(self.create_dummy_image()).decode('utf-8'),
            "bird_count": 2
        }
        
        print(f"🚨 고위험 탐지 생성:")
        print(f"   - 카메라: {detection['cctv_id']}")
        print(f"   - 신뢰도: {detection['confidence']} (RED 위험도)")
        print(f"   - 새 개체 수: {detection['bird_count']}")
        
        success = self.send_detection(detection)
        
        if success:
            print(f"✅ 고위험 알림 전송 성공! 🚨")
        else:
            print(f"❌ 고위험 알림 전송 실패!")
        
        return success
    
    def check_server_status(self) -> bool:
        """서버 상태 확인"""
        try:
            response = self.session.get(f"{self.server_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ 서버 연결 정상")
                return True
            else:
                print(f"⚠️ 서버 응답 이상: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("🚁 조류 충돌 방지 시스템 - 외부 모델 테스트")
    print("=" * 60)
    
    # 시뮬레이터 초기화
    simulator = BirdDetectionSimulator()
    
    # 서버 상태 확인
    if not simulator.check_server_status():
        print("❌ 서버가 실행되지 않았습니다. 백엔드를 먼저 시작해주세요.")
        return
    
    # 테스트 메뉴
    while True:
        print("\n" + "="*50)
        print("🎯 테스트 메뉴를 선택하세요:")
        print("1. 단일 탐지 테스트")
        print("2. 연속 탐지 테스트 (5개)")
        print("3. 고위험 시나리오 테스트")
        print("4. 대량 테스트 (20개)")
        print("5. 종료")
        print("="*50)
        
        choice = input("선택 (1-5): ").strip()
        
        if choice == "1":
            simulator.test_single_detection()
        
        elif choice == "2":
            simulator.test_multiple_detections(count=5, interval=1.5)
        
        elif choice == "3":
            simulator.test_high_risk_scenario()
        
        elif choice == "4":
            print("\n⚡ 대량 테스트 시작...")
            success, total = simulator.test_multiple_detections(count=20, interval=0.5)
            print(f"\n📊 대량 테스트 결과: {success}/{total} 성공 ({success/total*100:.1f}%)")
        
        elif choice == "5":
            print("👋 테스트 종료")
            break
        
        else:
            print("❌ 잘못된 선택입니다. 1-5 중에서 선택해주세요.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
