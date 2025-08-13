# CSV 데이터를 API로 전송하는 유틸리티
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path

class CSVToAPIConverter:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
    
    def process_csv_file(self, csv_path: str, cctv_id: str = "camera_01"):
        """
        CSV 파일을 읽어서 각 탐지 결과를 API로 전송
        
        Args:
            csv_path: CSV 파일 경로
            cctv_id: 카메라 ID (기본값: "camera_01")
        """
        df = pd.read_csv(csv_path)
        
        success_count = 0
        total_count = len(df)
        
        for idx, row in df.iterrows():
            # CSV 데이터를 API 형식으로 변환
            detection_data = {
                "cctv_id": cctv_id,
                "bbox": [row['x1'], row['y1'], row['x2'], row['y2']],
                "confidence": row['confidence'],
                "captured_at": datetime.now().isoformat(),
                "image_name": row['image_name'],
                "bird_count": 1
            }
            
            try:
                response = requests.post(
                    f"{self.server_url}/detect/result",
                    json=detection_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ [{idx+1}/{total_count}] {row['image_name']} 전송 성공")
                else:
                    print(f"❌ [{idx+1}/{total_count}] {row['image_name']} 전송 실패: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ [{idx+1}/{total_count}] {row['image_name']} 오류: {e}")
        
        print(f"\n📊 전송 완료: {success_count}/{total_count} 성공")
        return success_count, total_count

# 사용 예시
if __name__ == "__main__":
    converter = CSVToAPIConverter()
    
    # CSV 파일 처리
    csv_file = "detection_results.csv"  # 팀원이 보낸 CSV 파일
    success, total = converter.process_csv_file(csv_file)
    
    print(f"전체 {total}개 중 {success}개 성공적으로 전송됨")
