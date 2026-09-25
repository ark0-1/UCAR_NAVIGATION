cmake_minimum_required(VERSION 3.0.2)
project(ucar_navigation)

## Use C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(catkin REQUIRED)

set(ROS_DEPENDENCIES
        nav_msgs
        amcl
        move_base
        teb_local_planner
        )

find_package(catkin REQUIRED COMPONENTS ${ROS_DEPENDENCIES})

catkin_package(
        INCLUDE_DIRS
        LIBRARIES
        CATKIN_DEPENDS
        ${ROS_DEPENDENCIES}
)

include_directories(
        ${catkin_INCLUDE_DIRS}
)