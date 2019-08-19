<?php

# This php script will just take the JSON you posted, and send it to FarmOS
# For some reason, MicroPython couldn't send the exact same thing itself...
# This takes basic authentication, and the harvest JSON, and posts it to the farmOS log.json.
# The only thing stored here is your FarmOS url, so isn't too vulnerable.

if ($_SERVER['REQUEST_METHOD'] === 'POST'){
    $data = json_decode(file_get_contents('php://input'),true);

    $jsonArray = json_encode($data);

    $url = 'https://example.com/farmOS/log.json?type=farm_harvest';
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_USERPWD, $_SERVER['PHP_AUTH_USER'] . ":" . $_SERVER['PHP_AUTH_PW']);
    curl_setopt($ch,CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json',
        'Content-Length: ' . strlen($jsonArray)
        ));
    curl_setopt($ch,CURLOPT_POSTFIELDS, $jsonArray);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST,"POST");
    //b
    $response= curl_exec($ch);
    $err = curl_error($ch);
    $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);
    if ($err){
        echo "Curl error:" . $err;
        http_response_code($code);

    }else{
        http_response_code($code);
    }

}
