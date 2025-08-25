"""
CSV 기반 탐지 결과 DB 저장 및 프론트엔드 출력 테스트

🎯 목적:
- detection_results.csv 파일의 모든 탐지 결과를 DB에 저장
- 실제 이미지 파일과 함께 탐지 결과 업로드
- 프론트엔드에서 탐지 결과 조회 가능하도록 테스트

📋 CCTV ID 매핑:
- D02_20210628* → AIRPORT_CAM_D02_A (공항 D02 카메라 A지점)
- D02_20210721* → AIRPORT_CAM_D02_B (공항 D02 카메라 B지점)

🔧 실행 방법:
1. 백엔드 서버 실행: uvicorn app.main:app --reload --port 8000
2. 프론트엔드 실행: npm start
3. python csv_detection_test.py 실행
4. 프론트엔드에서 탐지 결과 확인
"""

import requests
import csv
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil

class CSVDetectionTester:
    """CSV 기반 탐지 결과 테스트 클래스"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # 이미지 디렉토리 경로
        self.image_dir = Path("detection_image")
        if not self.image_dir.exists():
            print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {self.image_dir}")
            sys.exit(1)
    
    def extract_cctv_id_from_image_name(self, image_name: str) -> str:
        """
        이미지 이름에서 CCTV ID 추출
        
        Args:
            image_name: 이미지 파일명 (예: D02_20210628090856_0000714_crop_000.png)
        
        Returns:
            str: CCTV ID (예: AIRPORT_CAM_D02_A)
        """
        if "20210628" in image_name:
            return "AIRPORT_CAM_D02_A"
        elif "20210721" in image_name:
            return "AIRPORT_CAM_D02_B"
        else:
            # 기본값
            return "AIRPORT_CAM_D02_DEFAULT"
    
    def load_csv_detections(self, csv_file: str = "detection_results.csv") -> List[Dict]:
        """CSV 파일에서 탐지 결과 로딩"""
        detections = []
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file}")
            return []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 숫자 필드 변환
                    detection = {
                        'image_index': int(row['image_index']),
                        'image_name': row['image_name'],
                        'object_id': int(row['object_id']),
                        'class_name': row['class_name'],
                        'confidence': float(row['confidence']),
                        'x1': float(row['x1']),
                        'y1': float(row['y1']),
                        'x2': float(row['x2']),
                        'y2': float(row['y2']),
                        'width': float(row['width']),
                        'height': float(row['height']),
                        'center_x': float(row['center_x']),
                        'center_y': float(row['center_y'])
                    }
                    detections.append(detection)
            
            print(f"✅ CSV에서 {len(detections)}개의 탐지 결과를 로딩했습니다.")
            return detections
            
        except Exception as e:
            print(f"❌ CSV 파일 로딩 실패: {e}")
            return []
    
    def upload_image(self, image_path: Path) -> Optional[str]:
        """이미지 파일 업로드"""
        if not image_path.exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
        
        try:
            # 이미지 업로드를 위한 별도의 세션 생성 (multipart/form-data용)
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/png')}
                # Content-Type 헤더를 제거하여 requests가 자동으로 multipart/form-data로 설정하도록 함
                headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                response = requests.post(
                    f"{self.server_url}/upload/image",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ 이미지 업로드 성공: {image_path.name} -> {result['url']}")
                    return result['url']
            
            print(f"❌ 이미지 업로드 실패: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ 이미지 업로드 오류: {e}")
            return None
    
    def csv_to_detection_format(self, csv_detection: Dict, cctv_id: str, frame_url: str) -> Dict:
        """CSV 탐지 데이터를 API 형식으로 변환"""
        
        # 바운딩 박스 [x, y, width, height] 형식
        bbox = [
            csv_detection['x1'],
            csv_detection['y1'], 
            csv_detection['width'],
            csv_detection['height']
        ]
        
        # 중심점 [center_x, center_y]
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
        
        return {
            "cctv_id": cctv_id,
            "bbox": bbox,
            "pos": pos,
            "risk": risk,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": frame_url,
            "bird_count": 1
        }
    
    def send_detection_result(self, detection_data: Dict) -> bool:
        """개별 탐지 결과 전송"""
        try:
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return True
            
            print(f"❌ 탐지 결과 전송 실패: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ 탐지 결과 전송 오류: {e}")
            return False
    
    def test_server_connection(self) -> bool:
        """서버 연결 테스트"""
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
    
    def get_detection_history(self, cctv_id: str) -> List[Dict]:
        """탐지 내역 조회"""
        try:
            response = self.session.get(f"{self.server_url}/detect/history/{cctv_id}")
            
            if response.status_code == 200:
                detections = response.json()
                print(f"✅ {cctv_id} 탐지 내역 조회 성공: {len(detections)}개")
                return detections
            else:
                print(f"❌ 탐지 내역 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 탐지 내역 조회 오류: {e}")
            return []
    
    def process_all_csv_detections(self, csv_file: str = "detection_results.csv") -> Dict[str, int]:
        """모든 CSV 탐지 결과 처리"""
        print("\n🚀 CSV 기반 탐지 결과 DB 저장 시작")
        print("=" * 60)
        
        # CSV 데이터 로딩
        detections = self.load_csv_detections(csv_file)
        if not detections:
            return {"total": 0, "success": 0, "failed": 0}
        
        results = {"total": len(detections), "success": 0, "failed": 0}
        cctv_stats = {}
        
        for i, csv_detection in enumerate(detections, 1):
            image_name = csv_detection['image_name']
            cctv_id = self.extract_cctv_id_from_image_name(image_name)
            
            print(f"\n📸 [{i}/{len(detections)}] 처리 중: {image_name}")
            print(f"   CCTV ID: {cctv_id}")
            print(f"   신뢰도: {csv_detection['confidence']:.3f}")
            
            # 통계 업데이트
            if cctv_id not in cctv_stats:
                cctv_stats[cctv_id] = 0
            
            # 이미지 업로드
            image_path = self.image_dir / image_name
            frame_url = self.upload_image(image_path)
            
            if not frame_url:
                print(f"   ❌ 이미지 업로드 실패, 탐지 결과 건너뜀")
                results["failed"] += 1
                continue
            
            # 탐지 결과 변환
            detection_data = self.csv_to_detection_format(csv_detection, cctv_id, frame_url)
            
            # 탐지 결과 전송
            if self.send_detection_result(detection_data):
                print(f"   ✅ 탐지 결과 저장 성공")
                results["success"] += 1
                cctv_stats[cctv_id] += 1
            else:
                print(f"   ❌ 탐지 결과 저장 실패")
                results["failed"] += 1
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 처리 결과 요약")
        print("=" * 60)
        print(f"전체: {results['total']}개")
        print(f"성공: {results['success']}개")
        print(f"실패: {results['failed']}개")
        
        print("\n📹 CCTV별 탐지 결과:")
        for cctv_id, count in cctv_stats.items():
            print(f"  {cctv_id}: {count}개")
        
        return results
    
    def verify_frontend_data(self) -> bool:
        """프론트엔드 데이터 확인"""
        print("\n🔍 프론트엔드 데이터 확인")
        print("=" * 40)
        
        # 각 CCTV의 탐지 내역 확인
        cctv_ids = ["AIRPORT_CAM_D02_A", "AIRPORT_CAM_D02_B"]
        
        for cctv_id in cctv_ids:
            detections = self.get_detection_history(cctv_id)
            
            if detections:
                print(f"\n✅ {cctv_id}: {len(detections)}개 탐지 결과")
                
                # 최근 탐지 결과 미리보기
                if len(detections) > 0:
                    latest = detections[0]
                    print(f"   최근 탐지: {latest.get('captured_at', 'N/A')}")
                    print(f"   위험도: {latest.get('risk', 'N/A')}")
                    print(f"   이미지: {latest.get('frame_url', 'N/A')}")
            else:
                print(f"❌ {cctv_id}: 탐지 결과 없음")
        
        return True
    
    def run_complete_test(self) -> bool:
        """전체 테스트 실행"""
        print("🎯 CSV 기반 탐지 결과 DB 저장 및 프론트엔드 테스트")
        print("=" * 80)
        
        # 1. 서버 연결 확인
        if not self.test_server_connection():
            return False
        
        # 2. 모든 CSV 탐지 결과 처리
        results = self.process_all_csv_detections()
        
        if results["success"] == 0:
            print("❌ 모든 탐지 결과 저장에 실패했습니다.")
            return False
        
        # 3. 프론트엔드 데이터 확인
        self.verify_frontend_data()
        
        # 4. 프론트엔드 접속 안내
        print("\n" + "=" * 80)
        print("🎉 테스트 완료!")
        print("=" * 80)
        print("📱 프론트엔드에서 결과 확인:")
        print("   1. 브라우저에서 http://localhost:3000 접속")
        print("   2. CCTV 목록에서 다음 카메라들 확인:")
        print("      - AIRPORT_CAM_D02_A (2021-06-28 데이터)")
        print("      - AIRPORT_CAM_D02_B (2021-07-21 데이터)")
        print("   3. 각 카메라 클릭하여 탐지 결과 및 이미지 확인")
        print("\n💡 참고:")
        print("   - 위험도는 신뢰도에 따라 자동 설정됩니다")
        print("   - 모든 이미지는 /frames/ 경로에 저장됩니다")
        print("   - 탐지 결과는 MongoDB에 저장됩니다")
        
        return True


def main():
    """메인 실행 함수"""
    tester = CSVDetectionTester("http://localhost:8000")
    
    # 현재 디렉토리 확인
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"CSV 파일 경로: {os.path.abspath('detection_results.csv')}")
    print(f"이미지 디렉토리: {os.path.abspath('detection_image')}")
    
    # 파일 존재 확인
    if not os.path.exists("detection_results.csv"):
        print("❌ detection_results.csv 파일이 없습니다.")
        print("   test 디렉토리에서 실행해주세요.")
        return
    
    if not os.path.exists("detection_image"):
        print("❌ detection_image 디렉토리가 없습니다.")
        return
    
    # 전체 테스트 실행
    success = tester.run_complete_test()
    
    if success:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 테스트 중 일부 문제가 발생했습니다.")


if __name__ == "__main__":
    main()
