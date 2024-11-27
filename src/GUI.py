import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rcl_interfaces.msg import Log
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import Point, PoseStamped, Quaternion, Pose
from serving_bot_interfaces.srv import PlaceOrder
from PyQt5.QtWidgets import QApplication
import math
from unit_ui import OrderUI
from unit_log import log
from unit_db import DB

class gui(Node):

    def __init__(self, ui_instance, log_instance, db_instance):
        super().__init__('gui')

        self.order_service = self.create_service(PlaceOrder,'order', self.order_callback)
        self.log_sub = self.create_subscription(Log, '/rosout', self.log_callback, 10)
        self.send_menu = ActionClient(self,NavigateToPose, 'navigate_to_pose')
        self.ui = ui_instance
        self.log = log_instance
        self.db = db_instance

        self.locate_tables = {
            '1': Pose(position = Point(x=1.0, y=1.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '2': Pose(position = Point(x=2.0, y=1.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '3': Pose(position = Point(x=3.0, y=1.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '4': Pose(position = Point(x=1.0, y=2.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '5': Pose(position = Point(x=2.0, y=2.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '6': Pose(position = Point(x=3.0, y=2.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '7': Pose(position = Point(x=1.0, y=3.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '8': Pose(position = Point(x=2.0, y=3.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            '9': Pose(position = Point(x=3.0, y=3.0),orientation = self.euler_to_quaternion(0, 0, 0)),
            'home': Pose(position = Point(x=0.0, y=0.0),orientation = self.euler_to_quaternion(0, 0, 0))
        }
        
    def euler_to_quaternion(self, roll, pitch, yaw):
        # Convert Euler angles to a quaternion
        qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
        qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
        qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
        qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
        return Quaternion(x=qx, y=qy, z=qz, w=qw)

    def log_callback(self, msg):
        log = self.log.update_log(msg)
        self.ui.update_log(log)

    def order_callback(self, request, respone):
        table_id = request.table_id
        order = request.order
        respone.msg = '주문이 완료되었습니다.'
        self.ui.update_order_data(table_id, order)
        self.send_db(table_id, order)

        if str(table_id) in self.locate_tables:
            target_pose = str(table_id)
            movement = PoseStamped()
            movement.header.frame_id = 'map'  # SLAM에서 사용되는 좌표계 (보통 'map' 프레임)
            movement.header.stamp = self.get_clock().now().to_msg()
            movement.pose.position.x = target_pose.position.x
            movement.pose.position.y = target_pose.position.y
            movement.pose.orientation = target_pose.orientation
            self._action_client.wait_for_server()
            self.get_logger().info(f'complete to serve')
            self._action_client.send_goal_async(
                movement,
                feedback_callback=self.feedback_callback
            ).add_done_callback(self.goal_response_callback)
        return respone
    
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"Current progress: {feedback.current_pose}")

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return
        self.get_logger().info('Goal accepted :)')
        goal_handle.get_result_async().add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result}')
        rclpy.shutdown()

    def send_db(self, table_id, order):
        self.db.update_db(table_id, order)



def main(args=None):
    rclpy.init(args=args)
    app = QApplication([])
    ui_instance = OrderUI()
    log_instance = log()
    db_instance = DB()
    node = gui(ui_instance, log_instance, db_instance)
    ui_instance.show()
    app.exec_()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()