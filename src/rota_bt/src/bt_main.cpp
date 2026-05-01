#include <chrono>
#include <thread>

#include <ament_index_cpp/get_package_share_directory.hpp>
#include <behaviortree_cpp_v3/bt_factory.h>
#include <behaviortree_cpp_v3/loggers/bt_cout_logger.h>
#include <rclcpp/rclcpp.hpp>

using namespace BT;

class CheckSensors : public SyncActionNode {
 public:
  CheckSensors(const std::string& name, const NodeConfiguration& config)
      : SyncActionNode(name, config) {}
  static PortsList providedPorts() { return {}; }
  NodeStatus tick() override {
    RCLCPP_DEBUG(rclcpp::get_logger("bt"), "CheckSensors: OK");
    return NodeStatus::SUCCESS;
  }
};

class CheckLocalization : public SyncActionNode {
 public:
  CheckLocalization(const std::string& name, const NodeConfiguration& config)
      : SyncActionNode(name, config) {}
  static PortsList providedPorts() { return {}; }
  NodeStatus tick() override {
    RCLCPP_DEBUG(rclcpp::get_logger("bt"), "CheckLocalization: OK");
    return NodeStatus::SUCCESS;
  }
};

class MoveToGoal : public SyncActionNode {
 public:
  MoveToGoal(const std::string& name, const NodeConfiguration& config)
      : SyncActionNode(name, config) {}
  static PortsList providedPorts() { return {}; }
  NodeStatus tick() override {
    RCLCPP_DEBUG(rclcpp::get_logger("bt"), "MoveToGoal: navigating");
    return NodeStatus::SUCCESS;
  }
};

class SafeStop : public SyncActionNode {
 public:
  SafeStop(const std::string& name, const NodeConfiguration& config)
      : SyncActionNode(name, config) {}
  static PortsList providedPorts() { return {}; }
  NodeStatus tick() override {
    RCLCPP_WARN(rclcpp::get_logger("bt"), "SafeStop: durduruluyor");
    return NodeStatus::SUCCESS;
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("rota_bt_node");

  BehaviorTreeFactory factory;
  factory.registerNodeType<CheckSensors>("CheckSensors");
  factory.registerNodeType<CheckLocalization>("CheckLocalization");
  factory.registerNodeType<MoveToGoal>("MoveToGoal");
  factory.registerNodeType<SafeStop>("SafeStop");

  const std::string xml_path =
      ament_index_cpp::get_package_share_directory("rota_bt") +
      "/bt_xml/main_tree.xml";
  auto tree = factory.createTreeFromFile(xml_path);
  StdCoutLogger logger(tree);

  RCLCPP_INFO(node->get_logger(),
              "BT.CPP agaci yuklendi (%s). 50 Hz tick basliyor.",
              xml_path.c_str());

  const auto period = std::chrono::milliseconds(20);
  int tick_count = 0;
  while (rclcpp::ok()) {
    tree.tickRoot();
    if (++tick_count % 50 == 0) {
      RCLCPP_INFO(node->get_logger(), "BT tick #%d", tick_count);
    }
    std::this_thread::sleep_for(period);
  }

  rclcpp::shutdown();
  return 0;
}
