// NUGUSEM_serverGUIDlg.cpp: 구현 파일
//

#include "pch.h"
#include "framework.h"
#include "NUGUSEM_serverGUI.h"
#include "NUGUSEM_serverGUIDlg.h"
#include "afxdialogex.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

#ifdef _DEBUG
#pragma comment(linker, "/ENTRY:WinMainCRTStartup /subsystem:console") // 빌드하여 실행했을 때, 콘솔도 함께 뜨도록 만들기 위한 명령
#endif

/* <global scope function... non- CNUGUSEMserverGUIDlg class context>
  desc: 클라이언트의 송신을 수신하기 위한, listen 역할을 담당하는 작업스레드.
*/
UINT ThreadForListening(LPVOID param)
{
	CNUGUSEMserverGUIDlg* pMain = (CNUGUSEMserverGUIDlg*)param;
	while (pMain->get_m_flagListenClientThread())
	{
		Sleep(1000);
		pMain->ListenClientAsync();
	}
	return 0;
}

//tcpip 관리자 호출 버튼 입력 시 전송되는 메시지를 수신대기
UINT ListeningForManager(LPVOID param)
{
	CNUGUSEMserverGUIDlg* pMain = (CNUGUSEMserverGUIDlg*)param;
	while (pMain->get_m_flagListenClientThread())
	{
		Sleep(1000);
		pMain->ListenClientAsync_Manager();
	}
	return 0;
}




// 응용 프로그램 정보에 사용되는 CAboutDlg 대화 상자입니다.

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

	// 대화 상자 데이터입니다.
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_ABOUTBOX };
#endif

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 지원입니다.

	// 구현입니다.
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(IDD_ABOUTBOX)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CNUGUSEMserverGUIDlg 대화 상자



CNUGUSEMserverGUIDlg::CNUGUSEMserverGUIDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_NUGUSEM_SERVERGUI_DIALOG, pParent)
	, m_strLog(_T(""))
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CNUGUSEMserverGUIDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Text(pDX, IDC_LOG, m_strLog);
	DDX_Control(pDX, IDC_LOG, m_controlLog);
}

BEGIN_MESSAGE_MAP(CNUGUSEMserverGUIDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_ABOUT, &CNUGUSEMserverGUIDlg::OnBnClickedAbout)
END_MESSAGE_MAP()



// CNUGUSEMserverGUIDlg 메시지 처리기

BOOL CNUGUSEMserverGUIDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 시스템 메뉴에 "정보..." 메뉴 항목을 추가합니다.

	// IDM_ABOUTBOX는 시스템 명령 범위에 있어야 합니다.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != nullptr)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// 이 대화 상자의 아이콘을 설정합니다.  응용 프로그램의 주 창이 대화 상자가 아닐 경우에는
	//  프레임워크가 이 작업을 자동으로 수행합니다.
	SetIcon(m_hIcon, TRUE);			// 큰 아이콘을 설정합니다.
	SetIcon(m_hIcon, FALSE);		// 작은 아이콘을 설정합니다.

	// TODO: 여기에 추가 초기화 작업을 추가합니다.

	m_flagListenClientThread = TRUE;
	m_nThread = AfxBeginThread(ThreadForListening, this);
	m_mThread = AfxBeginThread(ListeningForManager, this);


	return TRUE;  // 포커스를 컨트롤에 설정하지 않으면 TRUE를 반환합니다.
}

void CNUGUSEMserverGUIDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// 대화 상자에 최소화 단추를 추가할 경우 아이콘을 그리려면
//  아래 코드가 필요합니다.  문서/뷰 모델을 사용하는 MFC 애플리케이션의 경우에는
//  프레임워크에서 이 작업을 자동으로 수행합니다.

void CNUGUSEMserverGUIDlg::OnPaint()
{
	CPaintDC dc(this); // 그리기를 위한 디바이스 컨텍스트입니다.

	if (IsIconic())
	{
		CPaintDC dc(this); // 그리기를 위한 디바이스 컨텍스트입니다.

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 클라이언트 사각형에서 아이콘을 가운데에 맞춥니다.
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 아이콘을 그립니다.
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();

		dc.SetStretchBltMode(COLORONCOLOR); // 이미지를 축소나 확대를 경우 생기는 손실을 보정

		if (!m_cam_face_image.IsNull())
		{
			m_cam_face_image.Draw(dc, m_cam_face_rect); // 그림을 Picture Control 크기로 화면에 출력한다.	
		}
		if (!m_cam_face_image.IsNull())
		{
			m_cam_face_image.Draw(dc, m_cam_face_rect); // 그림을 Picture Control 크기로 화면에 출력한다.
		}
	}
}

// 사용자가 최소화된 창을 끄는 동안에 커서가 표시되도록 시스템에서
//  이 함수를 호출합니다.
HCURSOR CNUGUSEMserverGUIDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

// 비동기 소켓 통신 함수 정의
void CNUGUSEMserverGUIDlg::ListenClientAsync()
{
	CString str;
	server.run(str);

	if (server.get_Rflag() == 0) {
		// 이미지 출력용 png
		GetDlgItem(IDC_CAM_FACE)->GetWindowRect(m_cam_face_rect);
		ScreenToClient(m_cam_face_rect);
		PrintImage(_T("received_image.png"), m_cam_face_image, m_cam_face_rect);
		std::cout << "Image received" << std::endl;


		server.sendImageToClient(get_img_path());

		server.set_Rflag(-1);
	}
	else if (server.get_Rflag() == 1) {

		std::string input = std::string(CT2CA(str));
		int pos = 0;
		std::string uid = input.substr(0, input.find("@", 0));
		std::string log = input.substr(input.find("@", 0) + 1, input.length());

		std::cout << "uid: " << uid << std::endl;
		std::cout << "log: " << log << std::endl;

		//수신받은 UID로 DB에서 image path select
		CString img_path;
		if (DB.get_img_path(uid.c_str(), img_path))
		{
			set_img_path(img_path);
		}
		// Log String 수신 상황
		log = log + " UID: \"" + uid + "\" try to enter";
		log += "\r\n";
		int nLength = m_controlLog.GetWindowTextLength();
		m_controlLog.SetSel(nLength, nLength);
		m_controlLog.ReplaceSel(log.c_str());

	}
	else if (server.get_Rflag() == 4)//AUTH_LOG 수신
	{
		CString log = str;
		std::cout << "log: " << log << std::endl;
		log += "\r\n";

		int nLength = m_controlLog.GetWindowTextLength();
		m_controlLog.SetSel(nLength, nLength);
		m_controlLog.ReplaceSel(log);

	}
}

// 비동기 소켓 통신 함수 정의
void CNUGUSEMserverGUIDlg::ListenClientAsync_Manager()
{
	manager_server.run_manager();
	if (manager_server.get_image_upload_flag())
	{
		std::cout << "manager_server.get_image_upload_flag() !!!!!!!!!" << std::endl;
		GetDlgItem(IDC_CAM_FACE)->GetWindowRect(m_cam_face_rect);
		ScreenToClient(m_cam_face_rect);
		PrintImage(_T("received_image.png"), m_cam_face_image, m_cam_face_rect);
		std::cout << "Image received" << std::endl;
		manager_server.set_image_upload_flag(false);
	}
	if (manager_server.get_Manager_Req_flag()==1)
	{
		std::time_t currentTime;
		std::time(&currentTime);
		std::tm localTime;
		localtime_s(&localTime, &currentTime);
		// yyyy mm dd hh mm ss 형태의 문자열 생성
		char buffer[20];
		std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &localTime);
		// 결과를 string 변수에 담기
		std::string currentDateTime = buffer;


		std::string log;
		log = currentDateTime+ " 클라이언트로부터 관리자권한 출입문 개방 요청 발생\r\n";
		int nLength = m_controlLog.GetWindowTextLength();
		m_controlLog.SetSel(nLength, nLength);
		m_controlLog.ReplaceSel(log.c_str());

		UINT result = AfxMessageBox(_T("클라이언트로부터 관리자권한 출입문 개방 요청이 발생했습니다.\n개방 여부를 선택해주세요."), MB_YESNO | MB_ICONQUESTION);


		if (result == IDYES) {
			std::time(&currentTime);
			localtime_s(&localTime, &currentTime);
			std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &localTime);
			std::string currentDateTime = buffer;

			log = currentDateTime + " 클라이언트의 출입문 개방 요청 승인\r\n";
			int nLength = m_controlLog.GetWindowTextLength();
			m_controlLog.SetSel(nLength, nLength);
			m_controlLog.ReplaceSel(log.c_str());
			MessageBox(_T("요청을 승인했습니다.\n출입문을 개방합니다."));

			manager_server.set_Manager_com_flag(1);
			manager_server.set_Manager_Req_flag(2);
		}
		else if (result == IDNO) {
			std::time(&currentTime);
			localtime_s(&localTime, &currentTime);
			std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &localTime);
			std::string currentDateTime = buffer;

			log = currentDateTime + " 클라이언트의 출입문 개방 요청 거부\r\n";
			int nLength = m_controlLog.GetWindowTextLength();
			m_controlLog.SetSel(nLength, nLength);
			m_controlLog.ReplaceSel(log.c_str());
			MessageBox(_T("요청을 거부했습니다."));

			manager_server.set_Manager_com_flag(0);
			manager_server.set_Manager_Req_flag(2);
		}
	}
}

void CNUGUSEMserverGUIDlg::PrintImage(CString img_path, CImage& image_instance, CRect& image_rect)
{
	image_instance.~CImage();
	image_instance.Load(img_path);
	InvalidateRect(image_rect, TRUE);
}

BOOL CNUGUSEMserverGUIDlg::get_m_flagListenClientThread()
{
	return this->m_flagListenClientThread;
}

CString CNUGUSEMserverGUIDlg::get_img_path()
{
	return this->m_img_path;
}

void CNUGUSEMserverGUIDlg::set_img_path(CString img_path)
{
	this->m_img_path = img_path;
}

void CNUGUSEMserverGUIDlg::OnBnClickedAbout()
{
	CAboutDlg aboutDlg;
	aboutDlg.DoModal();
}