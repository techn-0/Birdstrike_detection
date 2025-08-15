"""
조류 탐지 결과 테스트 클라이언트
detection_results.csv 형식과 개별 탐지 결과 전송 기능 제공
"""

import requests
import csv
import json
from datetime import datetime
import os

class DetectionTester:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def send_csv_batch(self, csv_file_path: str = "detection_results.csv", cctv_id: str = "camera_01"):
        """
        CSV 파일의 모든 탐지 결과를 배치로 전송
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
        
        Returns:
            bool: 전송 성공 여부
        """
        
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return False
        
        detections = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    detection = {
                        "image_name": row['image_name'],
                        "object_id": int(row['object_id']),
                        "class_name": row['class_name'],
                        "x1": float(row['x1']),
                        "y1": float(row['y1']),
                        "x2": float(row['x2']),
                        "y2": float(row['y2']),
                        "confidence": float(row['confidence']),
                        "width": float(row['width']),
                        "height": float(row['height']),
                        "center_x": float(row['center_x']),
                        "center_y": float(row['center_y'])
                    }
                    detections.append(detection)
            
            # 배치 데이터 구성
            batch_data = {
                "detections": detections,
                "cctv_id": cctv_id,
                "captured_at": datetime.now().isoformat()
            }
            
            print(f"📂 CSV 파일 로딩 완료: {len(detections)}개 탐지 결과")
            print(f"📡 배치 전송 시작...")
            
            response = self.session.post(
                f"{self.server_url}/detect/batch",
                json=batch_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 배치 전송 성공: {len(detections)}개")
                return True
            else:
                print(f"❌ 전송 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 배치 처리 중 오류: {e}")
            return False
    
    def send_individual_detection(self, image_name: str, bbox: list, confidence: float, 
                                cctv_id: str = "camera_01", class_name: str = "bird"):
        """
        개별 탐지 결과 전송
        
        Args:
            image_name: 이미지 파일명
            bbox: [x1, y1, x2, y2] 바운딩 박스 좌표
            confidence: 신뢰도 (0.0 ~ 1.0)
            cctv_id: 카메라 ID
            class_name: 객체 클래스명
        
        Returns:
            bool: 전송 성공 여부
        """
        
        detection_data = {
            "cctv_id": cctv_id,
            "bbox": bbox,
            "confidence": confidence,
            "captured_at": datetime.now().isoformat(),
            "image_name": image_name,
            "bird_count": 1,
            "class_name": class_name
        }
        
        try:
            print(f"🔍 개별 탐지 결과 전송:")
            print(f"   이미지: {image_name}")
            print(f"   바운딩박스: {bbox}")
            print(f"   신뢰도: {confidence:.3f}")
            
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 개별 전송 성공")
                return True
            else:
                print(f"❌ 전송 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 개별 전송 중 오류: {e}")
            return False
    
    def send_csv_row_by_row(self, csv_file_path: str = "detection_results.csv", 
                          cctv_id: str = "camera_01", delay: float = 0.5):
        """
        CSV 파일의 탐지 결과를 하나씩 순차 전송
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
            delay: 전송 간격 (초)
        
        Returns:
            tuple: (성공 개수, 전체 개수)
        """
        
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return 0, 0
        
        success_count = 0
        total_count = 0
        
        try:
            import time
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    total_count += 1
                    
                    bbox = [
                        float(row['x1']),
                        float(row['y1']),
                        float(row['x2']),
                        float(row['y2'])
                    ]
                    
                    if self.send_individual_detection(
                        image_name=row['image_name'],
                        bbox=bbox,
                        confidence=float(row['confidence']),
                        cctv_id=cctv_id,
                        class_name=row['class_name']
                    ):
                        success_count += 1
                    
                    if delay > 0:
                        time.sleep(delay)
            
            print(f"\n📊 순차 전송 완료: {success_count}/{total_count} 성공")
            return success_count, total_count
            
        except Exception as e:
            print(f"❌ 순차 전송 중 오류: {e}")
            return success_count, total_count
    
    def test_server_connection(self):
        """서버 연결 테스트"""
        try:
            response = self.session.get(f"{self.server_url}/", timeout=5)
            if response.status_code == 200:
                print(f"✅ 서버 연결 성공: {self.server_url}")
                return True
            else:
                print(f"❌ 서버 응답 오류: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False

def main():
    """테스트 실행 예제"""
    
    # 테스터 초기화
    tester = DetectionTester("http://localhost:8000")
    
    # 서버 연결 확인
    if not tester.test_server_connection():
        print("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
        return
    
    print("\n" + "="*50)
    print("조류 탐지 결과 테스트 시작")
    print("="*50)
    
    # 1. CSV 배치 전송 테스트
    print("\n1️⃣ CSV 배치 전송 테스트")
    print("-" * 30)
    tester.send_csv_batch("detection_results.csv", "camera_01")
    
    # 2. 개별 탐지 결과 전송 테스트
    print("\n2️⃣ 개별 탐지 결과 전송 테스트")
    print("-" * 30)
    tester.send_individual_detection(
        image_name="test_image.jpg",
        bbox=[100.0, 150.0, 200.0, 250.0],
        confidence=0.85,
        cctv_id="camera_02"
    )
    
    # 3. CSV 순차 전송 테스트 (일부만)
    print("\n3️⃣ CSV 순차 전송 테스트 (처음 3개)")
    print("-" * 30)
    
    # 처음 3개만 테스트하기 위해 임시 CSV 생성
    import tempfile
    
    try:
        with open("detection_results.csv", 'r', encoding='utf-8') as original:
            lines = original.readlines()
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(lines[0])  # 헤더
            for i in range(1, min(4, len(lines))):  # 처음 3개 데이터
                temp_file.write(lines[i])
            temp_csv_path = temp_file.name
        
        success, total = tester.send_csv_row_by_row(temp_csv_path, "camera_03", delay=1.0)
        
        # 임시 파일 삭제
        os.unlink(temp_csv_path)
        
    except Exception as e:
        print(f"순차 전송 테스트 중 오류: {e}")
    
    print("\n" + "="*50)
    print("테스트 완료")
    print("="*50)

if __name__ == "__main__":
    main()
