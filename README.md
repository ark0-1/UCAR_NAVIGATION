# ucar_navigation

基于 ROS Navigation 栈的导航配置包，面向麦轮全向移动小车。整合雷达、底盘驱动、ICP 定位与 `move_base`，提供建图 / 导航的完整启动入口与调参文件。

## 功能

- **建图** — gmapping + 键盘遥控，参数针对室内雷达场景调优（限制远距离噪声、缩小更新阈值）
- **导航** — `move_base` + `teb_local_planner`，兼容 amcl / ICP 两种定位来源
- **多规划器切换** — 通过 `method` 参数一键切换 teb / dwa / eband / pid / mpc
- **代价地图** — 按机器人 footprint 与膨胀半径配置，局部地图使用滚动窗口

## 依赖

| 类型 | 依赖 |
|---|---|
| ROS | Melodic / Noetic，catkin 构建 |
| 官方包 | `move_base` `gmapping` `amcl` `map_server` `global_planner` `costmap_2d` `rviz` |
| 第三方 | [`teb_local_planner`](http://wiki.ros.org/teb_local_planner) |
| 本工作空间 | `ydlidar` `ucar_controller` `ucar_localization` `ep_teleop` |

`navigation.launch` 会 include 上表「本工作空间」的四个包，缺任意一个都无法启动。

## 编译

```bash
cd ~/ucar_ws
catkin_make          # 或 catkin build
source devel/setup.bash
```

## 目录结构

```
ucar_navigation/
├── launch/
│   ├── navigation.launch   # 导航总入口（雷达→底盘→TF→定位→move_base）
│   ├── gmapping.launch     # 建图
│   └── move_base.launch    # 仅 move_base + map_server
├── config/
│   └── teb/                # 规划器参数（目录名对应 method 参数）
│       ├── move_base_params.yaml
│       ├── costmap_common_params.yaml
│       ├── global_costmap_params.yaml
│       ├── local_costmap_params.yaml
│       └── base_local_planner_params*.yaml
├── map/                    # 地图（4 组 pgm + yaml）
├── rviz/nav_rviz.rviz      # 调试用 RViz 配置
└── scripts/draw_map.py     # 生成空白地图模板
```

## 使用方法

### 建图

```bash
roslaunch ucar_navigation gmapping.launch
```

默认同时拉起雷达、底盘驱动、TF 发布和键盘遥控。键盘控制（在 `keyboard.launch` 的终端中操作）：

| 按键 | 动作 | 按键 | 动作 |
|---|---|---|---|
| `I` | 前进 | `U` / `O` | 左前 / 右前 |
| `,` | 后退 | `M` / `.` | 左后 / 右后 |
| `J` / `L` | 左移 / 右移 | `K` | 停止 |

可通过 launch 参数关掉不需要的组件：

```bash
roslaunch ucar_navigation gmapping.launch use_lidar:=false use_keyboard_teleop:=false
```

建好后保存地图：

```bash
rosrun map_server map_saver -f $(rospack find ucar_navigation)/map/map
```

### 导航

```bash
roslaunch ucar_navigation navigation.launch
```

启动链路：`ydlidar` → `ucar_controller/base_driver` → `ucar_controller/tf_server` → `ucar_localization/scan_to_map_location` → `ucar_navigation/move_base`。

### 仅启动 move_base

```bash
roslaunch ucar_navigation move_base.launch method:=teb
```

`method` 决定两件事：加载 `config/<method>/` 下的参数，以及选择对应的局部规划器插件。launch 的 doc 列出 `teb` / `dwa` / `eband` / `pid` / `mpc`，但仓库中只提供了 `config/teb/`，**当前实际只能传 `teb`**（详见「已知问题」）。全局规划器固定为 `global_planner/GlobalPlanner`。

## 地图文件

`map_server` 默认加载 **`map_pro.yaml`**（在 `move_base.launch` 中指定）。

| 文件 | 分辨率 | 原点 | 用途 |
|---|---|---|---|
| `map_pro.yaml` | 0.025 m/px | (-10, -10) | **导航实际使用** |
| `map_update.yaml` | 0.025 m/px | (-10, -10) | 更新版本 |
| `map.yaml` | 0.01 m/px | (-2.25, -5.75) | 高分辨率小场景 |
| `gmapping.yaml` | 0.05 m/px | (-13.8, -12.2) | 建图原始输出 |

切换地图改 `move_base.launch` 里 `map_server` 的 `args` 即可。

## 关键参数

### move_base（`config/teb/move_base_params.yaml`）

| 参数 | 值 | 说明 |
|---|---|---|
| `controller_frequency` | 20.0 | 下发 `cmd_vel` 的频率 |
| `planner_frequency` | 10.0 | 全局重规划频率 |
| `controller_patience` | 15.0 | 等待有效控制指令的超时 |
| `planner_patience` | 5.0 | 等待有效全局路径的超时 |
| `oscillation_timeout` | 100.0 | 触发恢复行为的振荡时长 |
| `oscillation_distance` | 0.01 | 判定振荡的位移阈值 |

### 代价地图（`config/teb/costmap_common_params.yaml`）

| 参数 | 值 | 说明 |
|---|---|---|
| `footprint` | 0.26 × 0.20 m | 矩形轮廓 |
| `inflation_radius` | 0.12 | 膨胀半径 |
| `cost_scaling_factor` | 15 | 代价值衰减系数 |
| `obstacle_range` / `raytrace_range` | 3.0 | 障碍物标记 / 清除范围 |
| `resolution` | 0.01 | 栅格尺寸 |

### TEB 局部规划（`config/teb/base_local_planner_params.yaml`）

| 参数 | 值 | 说明 |
|---|---|---|
| `max_vel_x` / `max_vel_y` | 1.0 | 平移速度上限 |
| `max_vel_theta` | 2.0 | 角速度上限 |
| `min_obstacle_dist` | 0.07 | 最小避障距离 |
| `weight_viapoint` | 45.0 | 路径跟随权重 |
| `weight_obstacle` | 70.0 | 避障权重 |
| `weight_optimaltime` | 28 | 时间最优权重 |

## 已知问题

以下问题在阅读代码时发现，尚未修改，列在这里供参考：

1. **`method` 参数声称支持 5 种规划器，实际只有 `teb` 可用** — `move_base.launch` 中 `method` 的 doc 列出 `mpc, pid, teb, eband, dwa`，参数按 `config/$(arg method)/` 加载；但 `config/` 下只有 `teb/` 一个目录。传其他值会因找不到参数文件而启动失败。要么补齐各规划器的参数目录，要么把 doc 收窄到实际支持的范围。

2. **`move_base.launch` 中 `local_planner_params` 参数未被使用** — 该 arg 在第 15 行声明，但下方硬编码加载 `base_local_planner_params.yaml`，从未引用它。当前硬编码值与 arg 默认值一致，所以传参不生效但也不会出错。若想恢复可配置性，把加载语句的文件名改为 `$(arg local_planner_params)` 即可。

3. **代价地图与 TEB 的 footprint 尺寸不一致** — 两处声明的机器人轮廓不同：

   | 位置 | 参数 | 尺寸 |
   |---|---|---|
   | `costmap_common_params.yaml` | `footprint` | 0.26 × 0.20 m |
   | `base_local_planner_params.yaml` | `footprint_model.vertices` | 0.34 × 0.26 m |

   TEB 认为车比代价地图认为的大一圈。方向上偏保守（不会撞），但 `inflation_radius: 0.12` 是按 0.26×0.20 调的，窄通道里可能出现代价地图显示能过、TEB 却规划不出路径的情况。建议量出实测尺寸后统一。

4. **`local_costmap_params.yaml` 的 `global_frame` 设为 `map`** — 滚动窗口的局部代价地图通常用 `odom`，用 `map` 会让局部地图随定位跳变而移动。若依赖 `ucar_localization` 平滑发布的 `map→odom`，可能是刻意为之，但值得确认。

5. **`oscillation_distance: 0.01`** — 默认值为 0.5，此处极小，配合 100 秒的 `oscillation_timeout` 意味着长时间几乎不动就会触发恢复行为。若实际运行中频繁清理代价地图，可从这里排查。

6. **`scripts/draw_map.py` 与仓库地图不一致** — 脚本用相对路径 `../map/map.pgm` 保存，必须 `cd scripts` 后运行；且生成尺寸为 502×402，而仓库中的 `map.pgm` 是 502×602，说明后者已被手工修改过，重新运行脚本会覆盖丢失。

7. **`global_costmap_params.yaml` 未定义 `plugins`** — 走 costmap_2d 的默认插件列表，而 `local_costmap_params.yaml` 显式列出了 `obstacle_layer` + `inflation_layer`。行为上正常，但两处写法不一致，容易误读。

8. **`costmap_common_params.yaml` 末尾的 `map_type: costmap`** — Hydro 之前版本的遗留参数，现代 costmap_2d 已忽略。

9. **`package.xml` 的 `<license>` 仍为 `TODO`** — 公开仓库建议补上明确的许可证。

## License

待补充。
