@echo off
echo [1/6] Regi kontener takaritasa...
docker stop ros2_web_env >nul 2>&1
docker rm ros2_web_env >nul 2>&1

echo [2/6] ROS2 Docker kornyezet inditasa (2GB RAM)...
docker run -d -p 6080:80 -p 5900:5900 --shm-size=2g --name ros2_web_env -v "%cd%":/home/ubuntu/ros2_ws/src/turtle_chase tiryoh/ros2-desktop-vnc:humble

echo [3/6] Varakozas a rendszer indulasara (10 mp)...
timeout /t 10 /nobreak >nul

echo [4/6] Projekt buildelese...
docker exec ros2_web_env bash -c "source /opt/ros/humble/setup.bash && cd /home/ubuntu/ros2_ws && colcon build --symlink-install"
docker exec -u ubuntu ros2_web_env bash -c "echo 'source /home/ubuntu/ros2_ws/install/setup.bash' >> /home/ubuntu/.bashrc"

echo [5/6] VSCodium inditasa...
docker exec -u ubuntu ros2_web_env bash -c "mkdir -p /home/ubuntu/.config/VSCodium/User && echo '{\"window.newWindowDimensions\": \"maximized\"}' > /home/ubuntu/.config/VSCodium/User/settings.json"
docker exec -d -u ubuntu -e DISPLAY=:1 -e HOME=/home/ubuntu -e DONT_PROMPT_WSL_INSTALL=1 ros2_web_env bash -c "codium /home/ubuntu/ros2_ws/src/turtle_chase --no-sandbox --unity-launch"

echo [6/6] Bongeszo megnyitasa...
start http://127.0.0.1:6080/

echo.
echo KESZ! A projekt fut...
pause