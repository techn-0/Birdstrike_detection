#!/usr/bin/env python3
"""
실제 detection_results.csv 파일을 사용한 테스트
"""

from simple_test_client import load_csv_file, check_server

def main():
    print("🔍 실제 CSV 파일 테스트 시작...")
    
    # 서버 연결 확인
    if not check_server():
        print("❌ 서버 연결 실패")
        return
    
    # 실제 CSV 파일 테스트
    print("\n📄 detection_results.csv 파일 처리 중...")
    load_csv_file('detection_results.csv')

if __name__ == "__main__":
    main()
