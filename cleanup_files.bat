@echo off
REM 사용하지 않는 파일 정리 스크립트 (Windows)

echo 🗂️ Birdstrike Detection 프로젝트 파일 정리
echo ============================================

REM 1. 루트 디렉토리의 중복 파일들 삭제
echo 📁 루트 디렉토리 중복 파일 삭제...
if exist csv_test_client.py del csv_test_client.py
if exist simple_test_client.py del simple_test_client.py
if exist test_external_model.py del test_external_model.py

echo ✅ 루트 디렉토리 중복 파일 삭제 완료

REM 2. 구형 테스트 파일들 삭제
echo 📁 구형 테스트 파일 삭제...
if exist test\test_detect.py del test\test_detect.py
if exist test\test_real_csv.py del test\test_real_csv.py

echo ✅ 구형 테스트 파일 삭제 완료

REM 3. 백엔드 구형 파일들 삭제
echo 📁 백엔드 구형 파일 삭제...
if exist backend\csv_to_api.py del backend\csv_to_api.py
if exist backend\example_model_client.py del backend\example_model_client.py
if exist backend\example_model_client_simple.py del backend\example_model_client_simple.py

echo ✅ 백엔드 구형 파일 삭제 완료

REM 4. 레거시 문서 파일 삭제
echo 📁 레거시 문서 파일 삭제...
if exist TEST_README.md del TEST_README.md
if exist test\TEST_README.md del test\TEST_README.md

echo ✅ 레거시 문서 파일 삭제 완료

REM 5. 사용하지 않는 폴더 삭제 (주의: 백업 후 실행)
echo 📁 사용하지 않는 폴더 삭제...
REM if exist birdwatch-auth rmdir /s /q birdwatch-auth

echo 🎉 파일 정리 완료!
echo.
echo 📋 현재 활성 파일들:
echo   • test\simple_test_client.py - 메인 테스트 클라이언트
echo   • test\batch_test.py - 배치 테스트
echo   • test\quick_test.py - 빠른 테스트
echo   • test\csv_test_client.py - CSV 전용 테스트
echo   • backend\app\ - 메인 백엔드 애플리케이션
echo.
echo ⚠️  birdwatch-auth\ 폴더는 수동으로 확인 후 삭제하세요.

pause
