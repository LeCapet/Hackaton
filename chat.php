<?php
if(isset($_POST['message'])) {
    $message = $_POST['message'];
    $uploaded_files = [];

    if(isset($_FILES['files'])){
        $uploadDir = 'uploads/';
        if(!is_dir($uploadDir)) mkdir($uploadDir, 0777, true);

        foreach($_FILES['files']['tmp_name'] as $i => $tmpName){
            $dest = $uploadDir . basename($_FILES['files']['name'][$i]);
            move_uploaded_file($tmpName, $dest);
            $uploaded_files[] = $dest;
        }
    }

    $payload = json_encode(["message"=>$message, "files"=>$uploaded_files]);

    $cmd = "python3 p.py 2>&1";
    $descriptorspec = [
        0 => ["pipe","r"],
        1 => ["pipe","w"],
        2 => ["pipe","w"]
    ];

    $process = proc_open($cmd, $descriptorspec, $pipes);
    if(is_resource($process)){
        fwrite($pipes[0], $payload);
        fclose($pipes[0]);

        $output = stream_get_contents($pipes[1]);
        $errors = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);

        proc_close($process);

        header('Content-Type: application/json');
        if(!empty($errors)) $output = json_encode(["error"=>$errors]);
        echo $output;
    } else {
        echo json_encode(["error"=>"Impossible de lancer Python"]);
    }
}
?>
