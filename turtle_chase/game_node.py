import rclpy
from rclpy.node import Node
import random
import math
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill

class TurtleChaseGame(Node):
    def __init__(self):
        super().__init__('turtle_chase_game')
        
        # Játék állapot
        self.score = 0
        self.target_name = "prey"
        self.target_active = False
        self.target_x = 0.0
        self.target_y = 0.0
        
        # Paraméterek
        self.catch_distance = 0.5  # Milyen közel kell lenni az elkapáshoz
        self.pose_topic = '/turtle1/pose'

        # Kliensek a teknősök létrehozásához és törléséhez
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.kill_client = self.create_client(Kill, 'kill')

        # Feliratkozás a játékos pozíciójára
        self.subscription = self.create_subscription(
            Pose,
            self.pose_topic,
            self.pose_callback,
            10)

        # Várakozás a szolgáltatásokra
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not available, waiting...')
        while not self.kill_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Kill service not available, waiting...')

        # Játék indítása
        self.get_logger().info("🐢 TURTLE CHASE JÁTÉK ELINDULT 🐢")
        self.get_logger().info("Irányítsd a turtle1-et a célpontra a pontszerzéshez!")
        self.spawn_new_target()

    def pose_callback(self, msg):
        """
        Minden alkalommal lefut, amikor a fő teknős megmozdul. Ellenőrzi a távolságot.
        """
        if not self.target_active:
            return

        # Euklideszi távolság számítása
        distance = math.sqrt(
            (msg.x - self.target_x)**2 + 
            (msg.y - self.target_y)**2
        )

        # Ütközés (elkapás) ellenőrzése
        if distance < self.catch_distance:
            self.get_logger().info(f"Elkapva! Távolság: {distance:.2f}")
            self.capture_target()

    def spawn_new_target(self):
        """
        Létrehoz egy új célpontot véletlenszerű helyen.
        """
        self.target_x = random.uniform(1.0, 10.0)
        self.target_y = random.uniform(1.0, 10.0)
        
        request = Spawn.Request()
        request.x = self.target_x
        request.y = self.target_y
        request.theta = random.uniform(0, 6.28)
        request.name = self.target_name

        future = self.spawn_client.call_async(request)
        future.add_done_callback(self.spawn_callback)

    def spawn_callback(self, future):
        try:
            future.result()
            self.target_active = True
            self.get_logger().info(f"Új célpont itt: ({self.target_x:.1f}, {self.target_y:.1f})")
        except Exception as e:
            self.get_logger().error(f"Service hiba: {e}")

    def capture_target(self):
        """
        Elkapás kezelése: pontszám növelése, régi törlése, új kérése.
        """
        self.target_active = False
        self.score += 1
        self.get_logger().info(f"🎉 PONTSZÁM: {self.score} 🎉")

        # Jelenlegi célpont törlése
        request = Kill.Request()
        request.name = self.target_name
        
        future = self.kill_client.call_async(request)
        future.add_done_callback(self.kill_callback)

    def kill_callback(self, future):
        try:
            future.result()
            # Azonnal új létrehozása a törlés után
            self.spawn_new_target()
        except Exception as e:
            self.get_logger().error(f"Kill service hiba: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = TurtleChaseGame()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()