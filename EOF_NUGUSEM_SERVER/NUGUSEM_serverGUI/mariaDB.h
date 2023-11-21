// DB ¿¬°á
#pragma comment(lib, "libmariadb.lib")
#include "mysql/mysql.h"

#define CONNECT_IP "10.10.15.58"
#define DB_USER "EOF"
#define DB_PASSWORD "eofgo12#"
#define DB_PORT 3306
#define DB_NAME "nugusem"

class mariaDB
{
public:
	mariaDB();
	~mariaDB();

	void AttachDB();
	void DetachDB();
	BOOL get_img_path(CString UID, CString& img_path);

private:
	MYSQL Connect;
	MYSQL_RES* sql_query_result;
	MYSQL_ROW sql_row;
};
