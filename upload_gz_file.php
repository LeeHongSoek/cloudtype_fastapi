<?php
set_time_limit(0);

$uploadedfile = './uploaded_gz_file/'.$_FILES['upload'] ['name'];
$destination  = './uploaded_gz_file/';

move_uploaded_file($_FILES['upload']['tmp_name'],$uploadedfile);

chmod($uploadedfile, 0777); // 파일 권한을 777로 변경

$extract_command = "gunzip {$uploadedfile} "; // 압축 해제할 명령어
echo $extract_command ;

exec($extract_command); // 명령어 실행
?>
