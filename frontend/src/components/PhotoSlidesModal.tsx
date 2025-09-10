import React, { useState, useEffect, useRef, useCallback } from 'react';
import { PhotoSlidesData, PhotoSlideImage, DetectionLabel } from '../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  cctvId: string;
  cctvName: string;
}

const API = process.env.REACT_APP_API_HTTP;

export default function PhotoSlidesModal({ isOpen, onClose, cctvId, cctvName }: Props) {
  const [data, setData] = useState<PhotoSlidesData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1000); // 밀리초
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.3);
  const [showLabels, setShowLabels] = useState(true);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const loadPhotoSlidesData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API}/api/photo-slides/${cctvId}?confidence_threshold=${confidenceThreshold}`);
      if (!response.ok) {
        throw new Error('데이터를 불러올 수 없습니다.');
      }
      const result: PhotoSlidesData = await response.json();
      setData(result);
      setCurrentIndex(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [cctvId, confidenceThreshold]);

  // 데이터 로드
  useEffect(() => {
    if (isOpen && cctvId) {
      loadPhotoSlidesData();
    }
  }, [isOpen, cctvId, loadPhotoSlidesData]);

  // 자동 재생 제어
  useEffect(() => {
    if (isPlaying && data && data.images.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => (prev + 1) % data.images.length);
      }, speed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, speed, data]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // 이미지에 라벨 그리기
  const drawLabelsOnCanvas = (image: PhotoSlideImage, imgElement: HTMLImageElement) => {
    const canvas = canvasRef.current;
    if (!canvas || !showLabels) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 캔버스 크기를 이미지 크기에 맞춤
    canvas.width = imgElement.naturalWidth;
    canvas.height = imgElement.naturalHeight;

    // 이미지 그리기
    ctx.drawImage(imgElement, 0, 0);

    // 라벨 그리기
    image.labels.forEach((label: DetectionLabel) => {
      const { x1, y1, x2, y2, confidence, class_name } = label;
      
      // 바운딩 박스 그리기
      ctx.strokeStyle = confidence >= 0.7 ? '#ff0000' : confidence >= 0.5 ? '#ff8800' : '#ffff00';
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      // 라벨 텍스트 배경
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(x1, y1 - 25, 120, 25);

      // 라벨 텍스트
      ctx.fillStyle = '#ffffff';
      ctx.font = '14px Arial';
      ctx.fillText(`${class_name} ${(confidence * 100).toFixed(1)}%`, x1 + 5, y1 - 8);
    });
  };

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    if (data && data.images[currentIndex]) {
      drawLabelsOnCanvas(data.images[currentIndex], e.currentTarget);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-lg max-w-6xl max-h-[95vh] w-full mx-4 flex flex-col">
        {/* 헤더 */}
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-bold text-gray-800">
            📸 {cctvName} - 포토 슬라이드
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* 컨트롤 패널 */}
        <div className="p-4 border-b bg-gray-50">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <label className="text-sm">신뢰도 임계값:</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="w-20"
              />
              <span className="text-sm w-12">{(confidenceThreshold * 100).toFixed(0)}%</span>
            </div>
            
            <div className="flex items-center gap-2">
              <label className="text-sm">속도:</label>
              <select 
                value={speed} 
                onChange={(e) => setSpeed(Number(e.target.value))}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value={2000}>느림 (2초)</option>
                <option value={1000}>보통 (1초)</option>
                <option value={500}>빠름 (0.5초)</option>
                <option value={200}>매우 빠름 (0.2초)</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showLabels}
                onChange={(e) => setShowLabels(e.target.checked)}
                id="showLabels"
              />
              <label htmlFor="showLabels" className="text-sm">라벨 표시</label>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`px-4 py-2 rounded text-sm ${
                  isPlaying ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {isPlaying ? '⏸ 일시정지' : '▶ 재생'}
              </button>
              
              <button
                onClick={() => setCurrentIndex(0)}
                className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded text-sm"
              >
                ⏮ 처음
              </button>
            </div>
          </div>

          {data && (
            <div className="mt-2 text-sm text-gray-600">
              총 {data.total_images}개 이미지 | 현재: {currentIndex + 1}/{data.images.length} | 
              신뢰도 {(confidenceThreshold * 100).toFixed(0)}% 이상
            </div>
          )}
        </div>

        {/* 메인 콘텐츠 */}
        <div className="flex-1 p-4 overflow-auto">
          {loading && (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-500">데이터를 불러오는 중...</div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-64">
              <div className="text-red-500">{error}</div>
            </div>
          )}

          {data && data.images.length === 0 && (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-500">
                신뢰도 {(confidenceThreshold * 100).toFixed(0)}% 이상의 이미지가 없습니다.
              </div>
            </div>
          )}

          {data && data.images.length > 0 && (
            <div className="flex flex-col items-center">
              <div className="relative inline-block">
                <img
                  src={`${API}${data.images[currentIndex].image_url}`}
                  alt={data.images[currentIndex].image_name}
                  className="max-w-full max-h-[60vh] object-contain border rounded"
                  onLoad={handleImageLoad}
                  onError={(e) => {
                    console.error('이미지 로드 실패:', e);
                    setError('이미지를 불러올 수 없습니다.');
                  }}
                />
                
                {showLabels && (
                  <canvas 
                    ref={canvasRef}
                    className="absolute top-0 left-0 max-w-full max-h-[60vh] object-contain pointer-events-none"
                    style={{ zIndex: 1 }}
                  />
                )}
              </div>

              <div className="mt-4 text-center">
                <h3 className="text-lg font-semibold">{data.images[currentIndex].image_name}</h3>
                <p className="text-sm text-gray-600">
                  최대 신뢰도: {(data.images[currentIndex].max_confidence * 100).toFixed(1)}% | 
                  탐지 개수: {data.images[currentIndex].detection_count}개
                </p>
              </div>

              {/* 이미지 네비게이션 */}
              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
                  disabled={currentIndex === 0}
                  className="px-3 py-1 bg-gray-300 hover:bg-gray-400 rounded text-sm disabled:opacity-50"
                >
                  ← 이전
                </button>
                <button
                  onClick={() => setCurrentIndex(prev => Math.min(data.images.length - 1, prev + 1))}
                  disabled={currentIndex === data.images.length - 1}
                  className="px-3 py-1 bg-gray-300 hover:bg-gray-400 rounded text-sm disabled:opacity-50"
                >
                  다음 →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
