import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const { login, signup, loading } = useAuth();
  const [isSignupMode, setIsSignupMode] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    name: '',
    email: '',
    role: 'user' as 'user' | 'admin'
  });
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 기본 검증
    if (isSignupMode) {
      if (!formData.name || !formData.email) {
        setError('모든 필드를 입력해주세요.');
        return;
      }
      
      // 이메일 형식 검증
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('올바른 이메일 형식을 입력해주세요. (예: user@example.com)');
        return;
      }
      
      // 사용자명 길이 검증
      if (formData.username.length < 3) {
        setError('사용자명은 3자 이상이어야 합니다.');
        return;
      }
      
      // 이름 길이 검증
      if (formData.name.length < 2) {
        setError('이름은 2자 이상이어야 합니다.');
        return;
      }
      
      // 비밀번호 길이 검증
      if (formData.password.length < 6) {
        setError('비밀번호는 6자 이상이어야 합니다.');
        return;
      }
    }

    let success = false;

    if (isSignupMode) {
      success = await signup(formData);
      if (!success) {
        setError('회원가입에 실패했습니다. 이메일 형식과 입력 정보를 확인해주세요.');
      }
    } else {
      success = await login(formData.username, formData.password);
      if (!success) {
        setError('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.');
      }
    }

    if (success) {
      onClose();
      setFormData({
        username: '',
        password: '',
        name: '',
        email: '',
        role: 'user'
      });
      setIsSignupMode(false);
    }
  };

  const toggleMode = () => {
    setIsSignupMode(!isSignupMode);
    setError('');
    setFormData({
      username: '',
      password: '',
      name: '',
      email: '',
      role: 'user'
    });
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 9999 // 상단바보다 위에 표시
    }}>
      <div style={{
        backgroundColor: "white",
        borderRadius: "12px",
        padding: "24px",
        width: "100%",
        maxWidth: "400px",
        margin: "16px",
        boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
      }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "24px"
        }}>
          <h2 style={{
            margin: 0,
            fontSize: "24px",
            fontWeight: "bold",
            color: "#1f2937"
          }}>
            {isSignupMode ? '회원가입' : '로그인'}
          </h2>
          <button
            onClick={onClose}
            style={{
              backgroundColor: "transparent",
              border: "none",
              fontSize: "24px",
              color: "#6b7280",
              cursor: "pointer",
              padding: "4px",
              borderRadius: "6px",
              transition: "color 0.2s"
            }}
            onMouseOver={(e) => e.currentTarget.style.color = "#374151"}
            onMouseOut={(e) => e.currentTarget.style.color = "#6b7280"}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {isSignupMode && (
            <>
              <div>
                <label style={{
                  display: "block",
                  fontSize: "14px",
                  fontWeight: "500",
                  color: "#374151",
                  marginBottom: "4px"
                }}>
                  이름
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "2px solid #d1d5db",
                    borderRadius: "8px",
                    outline: "none",
                    transition: "border-color 0.2s",
                    fontSize: "14px",
                    boxSizing: "border-box"
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = "#3b82f6"}
                  onBlur={(e) => e.currentTarget.style.borderColor = "#d1d5db"}
                  required={isSignupMode}
                />
              </div>

              <div>
                <label style={{
                  display: "block",
                  fontSize: "14px",
                  fontWeight: "500",
                  color: "#374151",
                  marginBottom: "4px"
                }}>
                  이메일
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="user@example.com"
                  style={{
                    width: "100%",
                    padding: "12px",
                    border: "2px solid #d1d5db",
                    borderRadius: "8px",
                    outline: "none",
                    transition: "border-color 0.2s",
                    fontSize: "14px",
                    boxSizing: "border-box"
                  }}
                  onFocus={(e) => e.currentTarget.style.borderColor = "#3b82f6"}
                  onBlur={(e) => e.currentTarget.style.borderColor = "#d1d5db"}
                  required={isSignupMode}
                />
              </div>
            </>
          )}

          <div>
            <label style={{
              display: "block",
              fontSize: "14px",
              fontWeight: "500",
              color: "#374151",
              marginBottom: "4px"
            }}>
              사용자명
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="3자 이상"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #d1d5db",
                borderRadius: "8px",
                outline: "none",
                transition: "border-color 0.2s",
                fontSize: "14px",
                boxSizing: "border-box"
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = "#3b82f6"}
              onBlur={(e) => e.currentTarget.style.borderColor = "#d1d5db"}
              required
            />
          </div>

          <div>
            <label style={{
              display: "block",
              fontSize: "14px",
              fontWeight: "500",
              color: "#374151",
              marginBottom: "4px"
            }}>
              비밀번호
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="6자 이상"
              style={{
                width: "100%",
                padding: "12px",
                border: "2px solid #d1d5db",
                borderRadius: "8px",
                outline: "none",
                transition: "border-color 0.2s",
                fontSize: "14px",
                boxSizing: "border-box"
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = "#3b82f6"}
              onBlur={(e) => e.currentTarget.style.borderColor = "#d1d5db"}
              required
            />
          </div>

          {isSignupMode && (
            <div>
              <label style={{
                display: "block",
                fontSize: "14px",
                fontWeight: "500",
                color: "#374151",
                marginBottom: "4px"
              }}>
                역할
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "2px solid #d1d5db",
                  borderRadius: "8px",
                  outline: "none",
                  transition: "border-color 0.2s",
                  fontSize: "14px",
                  boxSizing: "border-box",
                  backgroundColor: "white"
                }}
                onFocus={(e) => e.currentTarget.style.borderColor = "#3b82f6"}
                onBlur={(e) => e.currentTarget.style.borderColor = "#d1d5db"}
              >
                <option value="user">사용자</option>
                <option value="admin">관리자</option>
              </select>
            </div>
          )}

          {error && (
            <div style={{
              color: "#dc2626",
              fontSize: "14px",
              backgroundColor: "#fef2f2",
              padding: "12px",
              borderRadius: "8px",
              border: "1px solid #fecaca"
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              backgroundColor: loading ? "#9ca3af" : "#3b82f6",
              color: "white",
              padding: "12px 16px",
              border: "none",
              borderRadius: "8px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "500",
              fontSize: "16px",
              transition: "background-color 0.2s"
            }}
            onMouseOver={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = "#2563eb";
            }}
            onMouseOut={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = "#3b82f6";
            }}
          >
            {loading ? '처리 중...' : (isSignupMode ? '회원가입' : '로그인')}
          </button>
        </form>

        <div style={{ marginTop: "16px", textAlign: "center" }}>
          <button
            onClick={toggleMode}
            style={{
              backgroundColor: "transparent",
              border: "none",
              color: "#3b82f6",
              fontSize: "14px",
              textDecoration: "underline",
              cursor: "pointer",
              fontWeight: "500",
              transition: "color 0.2s"
            }}
            onMouseOver={(e) => e.currentTarget.style.color = "#2563eb"}
            onMouseOut={(e) => e.currentTarget.style.color = "#3b82f6"}
          >
            {isSignupMode ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
          </button>
        </div>

        {/* 테스트용 계정 정보 */}
        <div style={{
          marginTop: "16px",
          padding: "12px",
          backgroundColor: "#f9fafb",
          borderRadius: "8px",
          fontSize: "12px",
          color: "#6b7280"
        }}>
          <div style={{ fontWeight: "600", marginBottom: "4px" }}>테스트 계정:</div>
          <div>관리자: admin / admin123</div>
          <div>사용자: user / user123</div>
        </div>
      </div>
    </div>
  );
};
