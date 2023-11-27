// NUGUSEM_serverGUIDlg.h: 헤더 파일
//

#pragma once

#include "Server.h"
#include "mariaDB.h"
#include <ctime>

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
	BOOL m_flagListenClientThread;//MFC Dlg init이 끝났을 때, 통신 쓰레드 시작용
	
	CRect m_cam_face_rect;//픽처컨트롤
	CImage m_cam_face_image;//픽처컨트롤

	CEdit m_controlLog;//에디트컨트롤
	CString m_strLog;//에디트컨트롤

	CWinThread* m_nThread;//일반 통신용 쓰레드
	CWinThread* m_mThread;/*manager thread*/

	CString m_img_path;

public:
	afx_msg void OnBnClickedAbout();

	Server server = Server();//일반 상황 통신용 포트: 8888
	Server manager_server = Server(MPORT);//매니저 호출 상황용 포트:8889

	mariaDB DB;

	// 비동기 소켓 통신을 위한 함수
	void ListenClientAsync();//일반 상황 통신용 쓰레드 함수
	void ListenClientAsync_Manager();//관리자 호출 상황 통신용 쓰레드 함수
	void PrintImage(CString img_path, CImage& image_instance, CRect& image_rect);

	BOOL get_m_flagListenClientThread();//MFC Dlg init이 끝났을 때, 통신 쓰레드 시작용 플래그 접근용

	CString get_img_path();
	void set_img_path(CString img_path);
};