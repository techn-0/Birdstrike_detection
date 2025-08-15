"""
조류 탐지 결과 저장 API 테스트 클라이언트
저장 API와 개별 탐지 결과 저장 API 테스트 제공
"""

import requests
import csv
import json
from datetime import datetime, timezone
import os
import time
from typing import List, Dict, Optional, Tuple

class DetectionStorageTester:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
        # 기본 헤더 설정
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def load_csv_data(self, csv_file_path: str = "detection_results.csv") -> List[Dict]:
        """
        CSV 파일에서 탐지 결과 데이터 로딩
        
        Args:
            csv_file_path: CSV 파일 경로
        
        Returns:
            List[Dict]: 탐지 결과 리스트
        """
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return []
        
        detections = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    detection = {
                        "image_index": int(row['image_index']),
                        "image_path": row['image_path'],
                        "image_name": row['image_name'],
                        "object_id": int(row['object_id']),
                        "class_name": row['class_name'],
                        "class_id": int(row['class_id']),
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
            
            print(f"📂 CSV 파일 로딩 완료: {len(detections)}개 탐지 결과")
            return detections
            
        except Exception as e:
            print(f"❌ CSV 파일 로딩 중 오류: {e}")
            return []
    
    def convert_csv_to_detection_format(self, csv_detection: Dict, cctv_id: str) -> Dict:
        """
        CSV 형식을 Detection API 형식으로 변환
        
        Args:
            csv_detection: CSV 탐지 데이터
            cctv_id: 카메라 ID
        
        Returns:
            Dict: Detection API 형식 데이터
        """
        # 바운딩 박스를 [x, y, w, h] 형식으로 변환
        bbox = [
            csv_detection['x1'],
            csv_detection['y1'],
            csv_detection['width'],
            csv_detection['height']
        ]
        
        # 중심점을 pos로 사용
        pos = [csv_detection['center_x'], csv_detection['center_y']]
        
        # 신뢰도 기반 위험도 설정
        confidence = csv_detection['confidence']
        if confidence >= 0.8:
            risk = "red"
        elif confidence >= 0.6:
            risk = "orange"
        elif confidence >= 0.4:
            risk = "yellow"
        else:
            risk = "green"
        
        detection_data = {
            "cctv_id": cctv_id,
            "bbox": bbox,
            "pos": pos,
            "risk": risk,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": f"frames/{csv_detection['image_name']}",
            "bird_count": 1
        }
        
        return detection_data
    
    def test_batch_storage_api(self, csv_file_path: str = "detection_results.csv", 
                              cctv_id: str = "camera_01") -> bool:
        """
        CSV 배치 저장 API 테스트 (/detect/batch)
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
        
        Returns:
            bool: 테스트 성공 여부
        """
        print(f"\n🔄 CSV 배치 저장 API 테스트 시작")
        print(f"   파일: {csv_file_path}")
        print(f"   카메라 ID: {cctv_id}")
        
        detections = self.load_csv_data(csv_file_path)
        if not detections:
            return False
        
        # DetectionBatch 형식으로 데이터 구성
        batch_data = {
            "detections": detections,
            "cctv_id": cctv_id,
            "captured_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            print(f"📡 배치 저장 요청 전송 중... ({len(detections)}개)")
            
            response = self.session.post(
                f"{self.server_url}/detect/batch",
                json=batch_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 배치 저장 성공!")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 배치 저장 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 배치 저장 API 테스트 중 오류: {e}")
            return False
    
    def test_individual_storage_api(self, csv_detection: Dict, cctv_id: str) -> bool:
        """
        개별 탐지 결과 저장 API 테스트 (/detect/result)
        
        Args:
            csv_detection: CSV 탐지 데이터
            cctv_id: 카메라 ID
        
        Returns:
            bool: 테스트 성공 여부
        """
        detection_data = self.convert_csv_to_detection_format(csv_detection, cctv_id)
        
        try:
            print(f"🔍 개별 저장 API 테스트:")
            print(f"   이미지: {csv_detection['image_name']}")
            print(f"   신뢰도: {csv_detection['confidence']:.3f}")
            print(f"   위험도: {detection_data['risk']}")
            
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 개별 저장 성공!")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 개별 저장 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 개별 저장 API 테스트 중 오류: {e}")
            return False
    
    def test_sequential_storage_api(self, csv_file_path: str = "detection_results.csv",
                                  cctv_id: str = "camera_01", delay: float = 0.5,
                                  max_count: Optional[int] = None) -> Tuple[int, int]:
        """
        CSV 파일의 탐지 결과를 개별 저장 API로 순차 전송
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
            delay: 전송 간격 (초)
            max_count: 최대 전송 개수 (None이면 전체)
        
        Returns:
            Tuple[int, int]: (성공 개수, 전체 개수)
        """
        print(f"\n🔄 순차 저장 API 테스트 시작")
        print(f"   파일: {csv_file_path}")
        print(f"   카메라 ID: {cctv_id}")
        print(f"   전송 간격: {delay}초")
        
        detections = self.load_csv_data(csv_file_path)
        if not detections:
            return 0, 0
        
        # 전송할 개수 제한
        if max_count:
            detections = detections[:max_count]
            print(f"   전송 제한: {len(detections)}개")
        
        success_count = 0
        total_count = len(detections)
        
        try:
            for i, detection in enumerate(detections, 1):
                print(f"\n[{i}/{total_count}] 개별 저장 테스트")
                
                if self.test_individual_storage_api(detection, cctv_id):
                    success_count += 1
                
                if delay > 0 and i < total_count:
                    print(f"⏳ {delay}초 대기...")
                    time.sleep(delay)
            
            print(f"\n📊 순차 저장 완료: {success_count}/{total_count} 성공")
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            print(f"   성공률: {success_rate:.1f}%")
            
            return success_count, total_count
            
        except Exception as e:
            print(f"❌ 순차 저장 테스트 중 오류: {e}")
            return success_count, total_count
    
    def test_detection_history_api(self, cctv_id: str) -> bool:
        """
        탐지 내역 조회 API 테스트 (/detect/history/{cctv_id})
        
        Args:
            cctv_id: 카메라 ID
        
        Returns:
            bool: 테스트 성공 여부
        """
        print(f"\n🔍 탐지 내역 조회 API 테스트")
        print(f"   카메라 ID: {cctv_id}")
        
        try:
            response = self.session.get(
                f"{self.server_url}/detect/history/{cctv_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                history = response.json()
                print(f"✅ 내역 조회 성공!")
                print(f"   저장된 탐지 결과: {len(history)}개")
                
                if history:
                    print(f"   최신 탐지: {history[0].get('captured_at', 'N/A')}")
                    print(f"   첫 번째 결과 예시:")
                    for key, value in list(history[0].items())[:5]:  # 처음 5개 필드만 표시
                        print(f"     {key}: {value}")
                    if len(history[0]) > 5:
                        print(f"     ... 및 {len(history[0]) - 5}개 필드 더")
                
                return True
            else:
                print(f"❌ 내역 조회 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 내역 조회 API 테스트 중 오류: {e}")
            return False
    
    def test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            print(f"🔗 서버 연결 테스트: {self.server_url}")
            response = self.session.get(f"{self.server_url}/ping", timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 서버 연결 성공!")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 서버 응답 오류: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            print("   서버가 실행 중인지 확인해주세요.")
            return False
    
    def create_sample_detection(self, image_name: str = "sample_bird.jpg", 
                              confidence: float = 0.75) -> Dict:
        """
        샘플 탐지 결과 생성
        
        Args:
            image_name: 이미지 파일명
            confidence: 신뢰도
        
        Returns:
            Dict: 샘플 탐지 데이터
        """
        return {
            "image_index": 999,
            "image_path": f"sample/{image_name}",
            "image_name": image_name,
            "object_id": 0,
            "class_name": "bird",
            "class_id": 0,
            "x1": 100.0,
            "y1": 150.0,
            "x2": 200.0,
            "y2": 250.0,
            "confidence": confidence,
            "width": 100.0,
            "height": 100.0,
            "center_x": 150.0,
            "center_y": 200.0
        }
    
    def run_comprehensive_test(self, csv_file_path: str = "detection_results.csv") -> Dict[str, bool]:
        """
        전체 저장 API 종합 테스트 실행
        
        Args:
            csv_file_path: CSV 파일 경로
        
        Returns:
            Dict[str, bool]: 각 테스트 결과
        """
        results = {}
        
        print("=" * 60)
        print("🧪 조류 탐지 결과 저장 API 종합 테스트")
        print("=" * 60)
        
        # 1. 서버 연결 테스트
        print("\n1️⃣ 서버 연결 테스트")
        print("-" * 40)
        results['connection'] = self.test_server_connection()
        
        if not results['connection']:
            print("\n❌ 서버 연결 실패로 테스트를 중단합니다.")
            return results
        
        # 2. 개별 샘플 저장 테스트
        print("\n2️⃣ 개별 샘플 저장 테스트")
        print("-" * 40)
        sample_detection = self.create_sample_detection("test_sample.jpg", 0.85)
        results['individual_sample'] = self.test_individual_storage_api(sample_detection, "test_camera")
        
        # 3. CSV 배치 저장 테스트
        print("\n3️⃣ CSV 배치 저장 테스트")
        print("-" * 40)
        results['batch_storage'] = self.test_batch_storage_api(csv_file_path, "camera_batch")
        
        # 4. CSV 순차 저장 테스트 (처음 3개만)
        print("\n4️⃣ CSV 순차 저장 테스트 (제한적)")
        print("-" * 40)
        success, total = self.test_sequential_storage_api(csv_file_path, "camera_sequential", 
                                                         delay=1.0, max_count=3)
        results['sequential_storage'] = (success == total and total > 0)
        
        # 5. 탐지 내역 조회 테스트
        print("\n5️⃣ 탐지 내역 조회 테스트")
        print("-" * 40)
        results['history_query'] = self.test_detection_history_api("camera_batch")
        
        # 6. 다른 카메라 내역 조회 테스트
        print("\n6️⃣ 다른 카메라 내역 조회 테스트")
        print("-" * 40)
        results['history_query_2'] = self.test_detection_history_api("camera_sequential")
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        passed = 0
        total_tests = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if passed_test:
                passed += 1
        
        print(f"\n총 {passed}/{total_tests}개 테스트 통과 ({(passed/total_tests)*100:.1f}%)")
        
        if passed == total_tests:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 로그를 확인해주세요.")
        
        return results

def main():
    """메인 테스트 실행 함수"""
    
    # 테스터 초기화
    tester = DetectionStorageTester("http://localhost:8000")
    
    # 종합 테스트 실행
    results = tester.run_comprehensive_test("detection_results.csv")
    
    # 추가 개별 테스트 예제
    if results.get('connection', False):
        print("\n" + "=" * 60)
        print("🔧 추가 개별 테스트 예제")
        print("=" * 60)
        
        # 고신뢰도 샘플 테스트
        print("\n🔥 고신뢰도 탐지 결과 테스트")
        high_conf_sample = tester.create_sample_detection("high_confidence_bird.jpg", 0.95)
        tester.test_individual_storage_api(high_conf_sample, "camera_high_conf")
        
        # 저신뢰도 샘플 테스트
        print("\n🟡 저신뢰도 탐지 결과 테스트")
        low_conf_sample = tester.create_sample_detection("low_confidence_bird.jpg", 0.35)
        tester.test_individual_storage_api(low_conf_sample, "camera_low_conf")

if __name__ == "__main__":
    main()
