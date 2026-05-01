cmake_minimum_required(VERSION 3.8)
project(rota_bt)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(rclcpp REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(rota_bt_node src/bt_main.cpp)
ament_target_dependencies(rota_bt_node
  rclcpp
  behaviortree_cpp_v3
  std_msgs
  ament_index_cpp
)

install(TARGETS rota_bt_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY bt_xml/
  DESTINATION share/${PROJECT_NAME}/bt_xml)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
