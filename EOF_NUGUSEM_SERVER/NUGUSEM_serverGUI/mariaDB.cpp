#include "pch.h"
#include "mariaDB.h"

mariaDB::mariaDB()
{
	AttachDB();
}

mariaDB::~mariaDB()
{
	DetachDB();
}

/*
  desc: DB를 연결한다.
  param: 연결할 DB의 name
*/
void mariaDB::AttachDB()
{
	mysql_init(&Connect); // Connect는 pre-compiled header에 전역변수로 정의되어 있음.

	if (mysql_real_connect(&Connect, CONNECT_IP, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, NULL, 0))
	{
#ifdef _DEBUG 
		printf("DB 연결성공!!!\n");
#endif
	}
	else
	{
#ifdef _DEBUG 
		printf("DB 연결실패...\n");
#endif
	}

	mysql_query(&Connect, "SET Names euckr"); // DB 문자 인코딩을 euckr로 셋팅
}

/*
  desc: DB를 연결을 해제한다.
  param: 연결할 DB의 name
*/
void mariaDB::DetachDB()
{
	mysql_close(&Connect);
#ifdef _DEBUG 
	printf("DB 연결해제...\n");
#endif
}

BOOL mariaDB::get_img_path(CString UID, CString& img_path)
{
	std::string query;
	query = std::string("SELECT img_path FROM person WHERE uid = '")
		+ std::string(CT2CA(UID)) + std::string("';");

	mysql_query(&Connect, query.c_str());
	sql_query_result = mysql_store_result(&Connect);

	if (mysql_num_rows(sql_query_result) == 0)
	{
		return FALSE;
	}
	else
	{
		sql_row = mysql_fetch_row(sql_query_result);
		if (sql_row != nullptr)
		{
			img_path = sql_row[0];
		}
	}
	mysql_free_result(sql_query_result);
	return TRUE;
}

