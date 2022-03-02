from __future__ import division
import os
import rospkg
import rospy

from geometry_msgs.msg import Twist
from python_qt_binding import loadUi
from python_qt_binding.QtCore import Qt, QTimer, Slot
from python_qt_binding.QtGui import QKeySequence
from python_qt_binding.QtWidgets import QShortcut, QWidget
from rqt_gui_py.plugin import Plugin


class HawkeyeSteering(Plugin):

    def __init__(self, context):
        super(HawkeyeSteering, self).__init__(context)
        self.setObjectName('HawkeyeSteering')

	topic = '/cmd_vel'
        self._publisher = rospy.Publisher(topic, Twist, queue_size=10)

        self._widget = QWidget()
        rp = rospkg.RosPack()
        ui_file = os.path.join(
            rp.get_path('hawkeye_steering'), 'resource', 'HawkeyeSteering.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('HawkeyeSteeringUi')
        if context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

	self.twist = Twist()

	self.shortcut_w = QShortcut(QKeySequence(Qt.Key_W), self._widget)
        self.shortcut_w.setContext(Qt.ApplicationShortcut)
        self.shortcut_w.activated.connect(self.up_pushed)
        self.shortcut_s = QShortcut(QKeySequence(Qt.Key_S), self._widget)
        self.shortcut_s.setContext(Qt.ApplicationShortcut)
        self.shortcut_s.activated.connect(self.down_pushed)
        self.shortcut_a = QShortcut(QKeySequence(Qt.Key_A), self._widget)
        self.shortcut_a.setContext(Qt.ApplicationShortcut)
        self.shortcut_a.activated.connect(self.left_pushed)
        self.shortcut_d = QShortcut(QKeySequence(Qt.Key_D), self._widget)
        self.shortcut_d.setContext(Qt.ApplicationShortcut)
        self.shortcut_d.activated.connect(self.right_pushed)

        self._update_parameter_timer = QTimer(self)
        self._update_parameter_timer.timeout.connect(
            self._send_zero)
        self._update_parameter_timer.start(100)
        self.zero_cmd_sent = False

        # Sliders and gui buttons
        self._widget.slider_linear_speed.valueChanged.connect(
            self._on_x_linear_slider_changed)
        self._widget.slider_angular_speed.valueChanged.connect(
            self._on_z_angular_slider_changed)

        # Buttons to control the speed sliders
        self._widget.button_linear_increase.pressed.connect(
            self._on_increase_x_linear_pressed)
        self._widget.button_linear_decrease.pressed.connect(
            self._on_decrease_x_linear_pressed)
        self._widget.button_angular_increase.pressed.connect(
            self._on_increase_z_angular_pressed)
        self._widget.button_angular_decrease.pressed.connect(
            self._on_decrease_z_angular_pressed)

        self._widget.label_linear_speed.setText(
            'Linear speed:\n%0.3f m/s' % (self._widget.slider_linear_speed.value() / 200))

        self._widget.label_angular_speed.setText(
            'Angular speed: %0.3f rad/s' % (self._widget.slider_angular_speed.value() / 200))

    def _send_zero(self):
        if not self.zero_cmd_sent:
	    self.twist.linear.x = 0
	    self.twist.linear.y = 0
	    self.twist.linear.z = 0
	    self.twist.angular.x = 0
	    self.twist.angular.y = 0
	    self.twist.angular.z = 0
            self.zero_cmd_sent = True
            self._publisher.publish(self.twist)

    # Button press definitions
    def up_pushed(self, checked = False):
	self.twist.linear.x = 1 * self._widget.slider_linear_speed.value() / 200
	self.twist.linear.y = 0
	self.twist.linear.z = 0
	self.twist.angular.x = 0
	self.twist.angular.y = 0
	self.twist.angular.z = 0
        self._publisher.publish(self.twist)

    def down_pushed(self, checked = False):
	self.twist.linear.x = -1 * self._widget.slider_linear_speed.value() / 200
	self.twist.linear.y = 0
	self.twist.linear.z = 0
	self.twist.angular.x = 0
	self.twist.angular.y = 0
	self.twist.angular.z = 0
        self._publisher.publish(self.twist)

    def left_pushed(self, checked = False):
	self.twist.linear.x = 0
	self.twist.linear.y = 0
	self.twist.linear.z = 0
	self.twist.angular.x = 0
	self.twist.angular.y = 0
	self.twist.angular.z = 1 * self._widget.slider_angular_speed.value() / 200
        self._publisher.publish(self.twist)

    def right_pushed(self, checked = False):
	self.twist.linear.x = 0
	self.twist.linear.y = 0
	self.twist.linear.z = 0
	self.twist.angular.x = 0
	self.twist.angular.y = 0
	self.twist.angular.z = -1 * self._widget.slider_angular_speed.value() / 200
        self._publisher.publish(self.twist)

    def arrow_released(self, checked = False):

	self.twist.linear.x = 0
	self.twist.linear.y = 0
	self.twist.linear.z = 0
	self.twist.angular.x = 0
	self.twist.angular.y = 0
	self.twist.angular.z = 0
        self._publisher.publish(self.twist)
        self.zero_cmd_sent = True

    def _on_x_linear_slider_changed(self):
        self._widget.label_linear_speed.setText(
            'Linear speed:\n%0.3f m/s' % (self._widget.slider_linear_speed.value() / 200))

    def _on_z_angular_slider_changed(self):
        self._widget.label_angular_speed.setText(
            'Angular speed: %0.3f rad/s' % (self._widget.slider_angular_speed.value() / 200))

    def _on_increase_x_linear_pressed(self):
        self._widget.slider_linear_speed.setValue(
            self._widget.slider_linear_speed.value() + self._widget.slider_linear_speed.singleStep())

    def _on_decrease_x_linear_pressed(self):
        self._widget.slider_linear_speed.setValue(
            self._widget.slider_linear_speed.value() - self._widget.slider_linear_speed.singleStep())

    def _on_increase_z_angular_pressed(self):
        self._widget.slider_angular_speed.setValue(
            self._widget.slider_angular_speed.value() + self._widget.slider_angular_speed.singleStep())

    def _on_decrease_z_angular_pressed(self):
        self._widget.slider_angular_speed.setValue(
            self._widget.slider_angular_speed.value() - self._widget.slider_angular_speed.singleStep())
