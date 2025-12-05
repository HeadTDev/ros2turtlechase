@echo off
echo ROS2 Kornyezet leallitasa...
docker stop ros2_web_env
docker rm ros2_web_env
echo.
echo A kornyezet leallt, a kontener torlodott.
pause