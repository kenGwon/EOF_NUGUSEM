// NUGUSEM_serverGUIDlg.h: 헤더 파일
//

#pragma once

#include "Server.h"
#include "mariaDB.h"

#define MESSAGE_LISTEN_CLIENT WM_USER + 1 // 사용자 정의 메세지

// CNUGUSEMserverGUIDlg 대화 상자
class CNUGUSEMserverGUIDlg : public CDialogEx
{
	// 생성입니다.
public:
	CNUGUSEMserverGUIDlg(CWnd* pParent = nullptr);	// 표준 생성자입니다.

	// 대화 상자 데이터입니다.
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_NUGUSEM_SERVERGUI_DIALOG };
#endif

protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 지원입니다.


	// 구현입니다.
protected:
	HICON m_hIcon;

	// 생성된 메시지 맵 함수
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()

private:
	BOOL m_flagListenClientThread;

	CRect m_cam_face_rect;
	CImage m_cam_face_image;

	CEdit m_controlLog;
	CString m_strLog;
	CWinThread* m_pThread;
	CWinThread* m_mThread;/*manager thread*/
	// 비동기 소켓 통신을 위한 변수 및 함수 추가
	std::mutex m_socketMutex;
	std::condition_variable m_condition;
	bool m_socketDataAvailable;
	CString m_img_path;





public:
	afx_msg void OnBnClickedOpen();
	afx_msg void OnBnClickedClose();
	BOOL get_m_flagListenClientThread();
	void PrintImage(CString img_path, CImage& image_instance, CRect& image_rect);
	void set_img_path(CString img_path);
	CString get_img_path();
	Server server = Server();
	Server manager_server = Server(8889);
	mariaDB DB;


	// 비동기 소켓 통신을 위한 함수
	void ListenClientAsync();
	void ListenClientAsync_Manager();
};