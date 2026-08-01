<?php
header('Content-Type: application/json');
echo json_encode(opcache_get_status(false));
