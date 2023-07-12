<?php
set_time_limit(0);

$uploadedfile = './uploaded_tar_file/'.$_FILES['upload'] ['name'];
$destination  = './uploaded_tar_file/';

move_uploaded_file($_FILES['upload']['tmp_name'],$uploadedfile);



// 파일 권한을 777로 변경
chmod($uploadedfile, 0777);

$chown_command = "chown mtns:mtns {$uploadedfile}";
exec($chown_command);


/*
// tar 파일의 소유자와 그룹 설정
$chmod_command = "chmod -R mtns:mtns {$uploadedfile}";
$chown_command = "chown mtns:mtns {$uploadedfile}";
$chgrp_command = "chgrp mtns {$uploadedfile}";

// 명령어 실행
exec($chmod_command);
exec($chown_command);
exec($chgrp_command);


$extracted_folder = $destination . 'extracted/';

// 압축 해제된 파일 및 디렉토리의 권한, 소유자, 그룹 설정
$chmod_command = "chmod -R mtns:mtns {$extracted_folder}";
$chown_command = "chown -R mtns:mtns {$extracted_folder}";
$chgrp_command = "chgrp -R mtns {$extracted_folder}";

// 명령어 실행
exec($chmod_command);
exec($chown_command);
exec($chgrp_command);

// 압축 해제할 명령어
$extract_command = "tar -xf {$uploadedfile} -C {$extracted_folder}";
echo $extract_command ;

// 명령어 실행
exec($extract_command);









// unzip 명령 실행
$command = "unzip -o {$uploadedfile} -d {$destination}";
echo $command ;
$output = shell_exec($command);



$uploadedFile = $_FILES['upload']['tmp_name']; // 업로드된 파일의 임시 경로
$destination = dirname(__FILE__) . '/db_file/';


if (empty($uploadedFile) || !file_exists($uploadedFile)) {
    echo 'No Uploaded file!.';
    exit;
}

// unzip 명령 실행
$command = "unzip -o {$uploadedFile} -d {$destination}";
echo $command ;
$output = shell_exec($command);

// 출력 확인
echo $output;
*/
?>
