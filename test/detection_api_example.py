"""
🔍 조류 탐지 API 사용 예시

이 스크립트는 탐지 결과 전송 팀원들이 실제로 사용할 수 있는 
간단한 API 호출 예시를 제공합니다.

사용법:
    python detection_api_example.py
"""

import requests
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List

class BirdDetectionAPI:
    """조류 탐지 결과 전송 API 클라이언트"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Args:
            server_url: 백엔드 서버 URL
        """
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json'
        })
    
    def check_server(self) -> bool:
        """서버 연결 상태 확인"""
        try:
            response = self.session.get(f"{self.server_url}/docs")
            if response.status_code == 200:
                print("✅ 서버 연결 성공")
                return True
            else:
                print(f"❌ 서버 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 오류: {e}")
            return False
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        이미지 파일 업로드
        
        Args:
            image_path: 업로드할 이미지 파일 경로
            
        Returns:
            업로드된 이미지 URL (성공 시) 또는 None (실패 시)
        """
        image_file = Path(image_path)
        
        if not image_file.exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
        
        try:
            with open(image_file, 'rb') as f:
                files = {'file': (image_file.name, f, 'image/png')}
                response = requests.post(
                    f"{self.server_url}/upload/image",
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ 이미지 업로드 성공: {result['url']}")
                    return result['url']
            
            print(f"❌ 이미지 업로드 실패: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ 이미지 업로드 오류: {e}")
            return None
    
    def calculate_risk(self, confidence: float) -> str:
        """
        신뢰도 기반 위험도 계산
        
        Args:
            confidence: 탐지 신뢰도 (0.0 ~ 1.0)
            
        Returns:
            위험도 ("red", "orange", "yellow", "green")
        """
        if confidence >= 0.8:
            return "red"
        elif confidence >= 0.6:
            return "orange"
        elif confidence >= 0.4:
            return "yellow"
        else:
            return "green"
    
    def send_detection(self, 
                      cctv_id: str,
                      bbox: List[float],
                      confidence: float,
                      frame_url: str,
                      bird_count: int = 1) -> bool:
        """
        탐지 결과 전송
        
        Args:
            cctv_id: CCTV ID (예: "AIRPORT_CAM_D02_A")
            bbox: 바운딩박스 [x, y, width, height]
            confidence: 탐지 신뢰도 (0.0 ~ 1.0)
            frame_url: 이미지 URL (upload_image 결과)
            bird_count: 탐지된 조류 수
            
        Returns:
            전송 성공 여부
        """
        # 중심점 계산
        center_x = bbox[0] + bbox[2] / 2
        center_y = bbox[1] + bbox[3] / 2
        
        # 위험도 계산
        risk = self.calculate_risk(confidence)
        
        # 탐지 결과 데이터 구성
        detection_data = {
            "cctv_id": cctv_id,
            "bbox": bbox,
            "pos": [center_x, center_y],
            "risk": risk,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": frame_url,
            "bird_count": bird_count
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ 탐지 결과 전송 성공 (위험도: {risk})")
                    return True
            
            print(f"❌ 탐지 결과 전송 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ 탐지 결과 전송 오류: {e}")
            return False
    
    def send_detection_with_image(self,
                                 cctv_id: str,
                                 image_path: str,
                                 bbox: List[float],
                                 confidence: float,
                                 bird_count: int = 1) -> bool:
        """
        이미지 업로드와 탐지 결과 전송을 한 번에 처리
        
        Args:
            cctv_id: CCTV ID
            image_path: 이미지 파일 경로
            bbox: 바운딩박스 [x, y, width, height]
            confidence: 탐지 신뢰도
            bird_count: 탐지된 조류 수
            
        Returns:
            전송 성공 여부
        """
        # 1. 이미지 업로드
        frame_url = self.upload_image(image_path)
        if not frame_url:
            return False
        
        # 2. 탐지 결과 전송
        return self.send_detection(cctv_id, bbox, confidence, frame_url, bird_count)
    
    def get_detection_history(self, cctv_id: str) -> List[Dict]:
        """
        특정 CCTV의 탐지 내역 조회
        
        Args:
            cctv_id: CCTV ID
            
        Returns:
            탐지 내역 리스트
        """
        try:
            response = self.session.get(f"{self.server_url}/detect/history/{cctv_id}")
            
            if response.status_code == 200:
                detections = response.json()
                print(f"✅ {cctv_id} 탐지 내역: {len(detections)}개")
                return detections
            else:
                print(f"❌ 탐지 내역 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 탐지 내역 조회 오류: {e}")
            return []


def example_usage():
    """사용 예시"""
    print("🔍 조류 탐지 API 사용 예시")
    print("=" * 50)
    
    # API 클라이언트 초기화
    api = BirdDetectionAPI("http://localhost:8000")
    
    # 서버 연결 확인
    if not api.check_server():
        print("서버가 실행되지 않았습니다. 백엔드를 먼저 실행해주세요.")
        return
    
    print("\n📤 탐지 결과 전송 예시")
    print("-" * 30)
    
    # 예시 1: 이미지 없이 탐지 결과만 전송
    print("\n1️⃣ 탐지 결과만 전송 (이미지 없음)")
    success = api.send_detection(
        cctv_id="AIRPORT_CAM_D02_A",
        bbox=[100, 150, 50, 30],  # [x, y, width, height]
        confidence=0.85,
        frame_url="/frames/example.png"  # 가상의 이미지 URL
    )
    
    if success:
        print("   ✅ 전송 완료")
    
    # 예시 2: 실제 이미지 파일이 있다면 (파일 존재 시에만)
    print("\n2️⃣ 이미지와 함께 탐지 결과 전송")
    sample_image = "detection_image/D02_20210628090856_0000714_crop_000.png"
    
    if Path(sample_image).exists():
        success = api.send_detection_with_image(
            cctv_id="AIRPORT_CAM_D02_A",
            image_path=sample_image,
            bbox=[508.83, 534.93, 15.68, 8.19],
            confidence=0.272,
            bird_count=1
        )
        
        if success:
            print("   ✅ 이미지와 함께 전송 완료")
    else:
        print(f"   ⚠️ 샘플 이미지를 찾을 수 없습니다: {sample_image}")
    
    # 예시 3: 탐지 내역 조회
    print("\n3️⃣ 탐지 내역 조회")
    detections = api.get_detection_history("AIRPORT_CAM_D02_A")
    
    if detections:
        print(f"   📊 최근 탐지 결과:")
        for i, detection in enumerate(detections[:3]):  # 최근 3개만 표시
            risk = detection.get('risk', 'N/A')
            time = detection.get('captured_at', 'N/A')
            count = detection.get('bird_count', 1)
            print(f"      {i+1}. 위험도: {risk}, 시간: {time}, 조류수: {count}")
    
    print("\n🎉 예시 완료!")
    print("\n💡 프론트엔드 확인: http://localhost:3000")


def custom_detection_example():
    """사용자 정의 탐지 결과 전송 예시"""
    print("\n🎯 사용자 정의 탐지 결과 전송")
    print("=" * 40)
    
    api = BirdDetectionAPI()
    
    # 사용자 입력을 받아 탐지 결과 전송
    print("탐지 결과 정보를 입력하세요:")
    
    try:
        cctv_id = input("CCTV ID (예: AIRPORT_CAM_D02_A): ").strip()
        if not cctv_id:
            cctv_id = "AIRPORT_CAM_D02_A"
        
        confidence = float(input("신뢰도 (0.0-1.0, 예: 0.85): ").strip() or "0.85")
        
        # 바운딩박스 입력
        print("바운딩박스 좌표 (x,y,width,height):")
        x = float(input("  X: ").strip() or "100")
        y = float(input("  Y: ").strip() or "150") 
        width = float(input("  Width: ").strip() or "50")
        height = float(input("  Height: ").strip() or "30")
        
        bbox = [x, y, width, height]
        bird_count = int(input("조류 수 (예: 1): ").strip() or "1")
        
        # 탐지 결과 전송
        success = api.send_detection(
            cctv_id=cctv_id,
            bbox=bbox,
            confidence=confidence,
            frame_url="/frames/custom_detection.png",
            bird_count=bird_count
        )
        
        if success:
            print("✅ 사용자 정의 탐지 결과 전송 완료!")
        else:
            print("❌ 전송 실패")
            
    except ValueError as e:
        print(f"❌ 입력 오류: {e}")
    except KeyboardInterrupt:
        print("\n사용자에 의해 취소되었습니다.")


if __name__ == "__main__":
    """메인 실행부"""
    print("🚀 조류 탐지 API 클라이언트")
    print("=" * 50)
    print("1. 기본 예시 실행")
    print("2. 사용자 정의 탐지 결과 전송") 
    print("3. 종료")
    
    try:
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == "1":
            example_usage()
        elif choice == "2":
            custom_detection_example()
        elif choice == "3":
            print("프로그램을 종료합니다.")
        else:
            print("잘못된 선택입니다. 기본 예시를 실행합니다.")
            example_usage()
            
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
