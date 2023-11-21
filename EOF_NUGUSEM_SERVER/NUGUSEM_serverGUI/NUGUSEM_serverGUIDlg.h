// NUGUSEM_serverGUIDlg.h: 헤더 파일
//

#pragma once

#include "Server.h"

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

public:
	afx_msg void OnBnClickedOpen();
	afx_msg void OnBnClickedClose();
	LRESULT get_TCPIP_data(WPARAM wParam, LPARAM lParam);
	BOOL get_m_flagListenClientThread();
	Server server;
};