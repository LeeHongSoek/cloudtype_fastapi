from ftplib import FTP, error_perm

def create_directory(ftp, directory):
    """FTP 서버에 디렉토리를 생성합니다."""
    parts = directory.split('/')
    for part in parts:
        try:
            ftp.cwd(part)
        except:
            ftp.mkd(part)
            ftp.cwd(part)


# Connect to the FTP server
ftp = FTP('ftp.drivehq.com')
ftp.login(user='LeeHongSoek', passwd='leehs1181!')


# 원하는 디렉토리 경로
directory = '/sqlite'

# 디렉토리 생성
create_directory(ftp, directory)

# 생성된 디렉토리로 이동
ftp.cwd(directory)


# List the files in the current directory
files = ftp.nlst()
for file in files:
    print(file)

# Download a file
filename = 'lhs_stock.db'
try:
    with open(filename, 'wb') as file:
        ftp.retrbinary('RETR ' + filename, file.write)
    print("File downloaded successfully.")
except error_perm as e:
    if str(e).startswith("550"):
        print("File does not exist.")
    else:
        print("Error occurred during file download:", str(e))



# Upload a file
filename = 'lhs_stock.db'
try:
    with open(filename, 'rb') as file:
        ftp.storbinary('STOR ' + filename, file)
    print("File uploaded successfully.")
except error_perm as e:
    if str(e).startswith("550"):
        print("Error: Permission denied or file upload failed.")
    else:
        print("Error occurred during file upload:", str(e))


# Disconnect from the FTP server
ftp.quit()
