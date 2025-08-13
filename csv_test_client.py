"""
실제 CSV 탐지 결과를 API로 전송하는 테스트 스크립트
팀원이 보낸 detection_results.csv 파일을 직접 사용
"""

import requests
import csv
from datetime import datetime
import os
import time

class CSVDetectionTester:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def send_csv_detections(self, csv_file_path: str, cctv_id: str = "camera_01", delay: float = 1.0):
        """
        CSV 파일의 탐지 결과를 순차적으로 서버에 전송
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 사용할 카메라 ID
            delay: 전송 간격 (초)
        """
        
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return
        
        print(f"📂 CSV 파일 로딩: {csv_file_path}")
        print(f"📡 대상 서버: {self.server_url}")
        print(f"📹 카메라 ID: {cctv_id}")
        print(f"⏱️ 전송 간격: {delay}초")
        print("-" * 50)
        
        success_count = 0
        total_count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    total_count += 1
                    
                    # CSV 데이터를 API 형식으로 변환
                    detection_data = {
                        "cctv_id": cctv_id,
                        "bbox": [
                            float(row['x1']),
                            float(row['y1']),
                            float(row['x2']),
                            float(row['y2'])
                        ],
                        "confidence": float(row['confidence']),
                        "captured_at": datetime.now().isoformat(),
                        "image_name": row['image_name'],
                        "bird_count": 1
                    }
                    
                    print(f"\n[{total_count}] 🔍 탐지 결과 전송 중...")
                    print(f"  이미지: {row['image_name']}")
                    print(f"  바운딩박스: [{detection_data['bbox'][0]:.1f}, {detection_data['bbox'][1]:.1f}, {detection_data['bbox'][2]:.1f}, {detection_data['bbox'][3]:.1f}]")
                    print(f"  신뢰도: {detection_data['confidence']:.3f}")
                    
                    # API 전송
                    if self.send_detection(detection_data):
                        success_count += 1
                        print(f"  ✅ 전송 성공")
                    else:
                        print(f"  ❌ 전송 실패")
                    
                    # 다음 전송까지 대기
                    if total_count < self.count_csv_rows(csv_file_path):
                        time.sleep(delay)
        
        except Exception as e:
            print(f"❌ CSV 처리 중 오류 발생: {e}")
        
        print("\n" + "="*50)
        print(f"📊 전송 완료: {success_count}/{total_count} 성공")
        print(f"📈 성공률: {success_count/total_count*100:.1f}%" if total_count > 0 else "성공률: 0%")
        
        return success_count, total_count
    
    def send_detection(self, detection_data: dict) -> bool:
        """개별 탐지 결과 전송"""
        try:
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("ok", False)
            else:
                print(f"    HTTP 에러 {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    전송 오류: {e}")
            return False
    
    def count_csv_rows(self, csv_file_path: str) -> int:
        """CSV 파일의 행 수 계산"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                return sum(1 for line in csv.DictReader(file))
        except:
            return 0
    
    def preview_csv_data(self, csv_file_path: str, max_rows: int = 3):
        """CSV 데이터 미리보기"""
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return
        
        print(f"📋 CSV 데이터 미리보기 (최대 {max_rows}개)")
        print("-" * 50)
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for i, row in enumerate(csv_reader):
                    if i >= max_rows:
                        break
                    
                    print(f"\n[{i+1}] {row['image_name']}")
                    print(f"  바운딩박스: [{row['x1']}, {row['y1']}, {row['x2']}, {row['y2']}]")
                    print(f"  신뢰도: {row['confidence']}")
                    print(f"  중심점: ({row['center_x']}, {row['center_y']})")
                
                total_rows = self.count_csv_rows(csv_file_path)
                print(f"\n📊 총 {total_rows}개의 탐지 결과가 있습니다.")
                
        except Exception as e:
            print(f"❌ CSV 읽기 오류: {e}")

def main():
    print("=" * 60)
    print("🚁 조류 탐지 CSV 데이터 전송 테스트")
    print("=" * 60)
    
    # CSV 파일 경로 설정
    csv_file = "detection_results.csv"  # 팀원이 보낸 CSV 파일
    
    # 테스터 초기화
    tester = CSVDetectionTester()
    
    # CSV 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file}")
        print("💡 detection_results.csv 파일을 같은 폴더에 복사해주세요.")
        return
    
    # 데이터 미리보기
    tester.preview_csv_data(csv_file)
    
    # 사용자 입력
    print("\n" + "="*50)
    print("📋 전송 옵션을 선택하세요:")
    print("1. 전체 데이터 전송 (느린 속도 - 2초 간격)")
    print("2. 전체 데이터 전송 (빠른 속도 - 0.5초 간격)")
    print("3. 첫 3개만 테스트 전송")
    print("4. 종료")
    
    choice = input("선택 (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 전체 데이터 전송 시작 (느린 속도)...")
        tester.send_csv_detections(csv_file, delay=2.0)
    
    elif choice == "2":
        print("\n⚡ 전체 데이터 전송 시작 (빠른 속도)...")
        tester.send_csv_detections(csv_file, delay=0.5)
    
    elif choice == "3":
        print("\n🔍 첫 3개 데이터 테스트 전송...")
        # 임시 CSV 파일 생성 (첫 3개 행만)
        temp_csv = "temp_test.csv"
        try:
            with open(csv_file, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                with open(temp_csv, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    # 헤더 복사
                    header = next(reader)
                    writer.writerow(header)
                    # 첫 3개 행 복사
                    for i, row in enumerate(reader):
                        if i >= 3:
                            break
                        writer.writerow(row)
            
            tester.send_csv_detections(temp_csv, delay=1.0)
            os.remove(temp_csv)  # 임시 파일 삭제
            
        except Exception as e:
            print(f"❌ 테스트 파일 생성 실패: {e}")
    
    elif choice == "4":
        print("👋 프로그램 종료")
    
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
