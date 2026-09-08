# Unitree Go2 ROS 2 - CHAMP Controller

> ROS 2 Humble package for the Unitree Go2 quadruped robot using the CHAMP controller framework with Ignition Fortress (Gazebo) simulation. Features teleoperation, 3D LiDAR (Velodyne), IMU, and 2D LiDAR support.

## Unitree Go2:
<div style="display: flex; gap: 50px;">
  <img src="https://oss-global-cdn.unitree.com/static/c487f93e06954100a44fac4442b94d94_288x238.png" width="250" />
  <img src=".docs/gz.png" width="350" /> 
</div>

> Unitree Robotics is focusing on the R&D, production, and sales of consumer and industry-class high-performance general-purpose legged and humanoid robots, six-axis manipulators, and so on. They attach great importance to independent research and development and technological innovation, fully self-researching key core robot components such as motors, reducers, controllers, LIDAR and high-performance perception and motion control algorithms, integrating the entire robotics industry chain.

## CHAMP Controller:
![champ](https://raw.githubusercontent.com/chvmp/champ/master/docs/images/robots.gif)

> CHAMP is an open source development framework for building new quadrupedal robots and developing new control algorithms. The control framework is based on [*"Hierarchical controller for highly dynamic locomotion utilizing pattern modulation and impedance control : implementation on the MIT Cheetah robot"*](https://dspace.mit.edu/handle/1721.1/85490).

## Resources:
- [Go2 Description (URDF model)](https://github.com/unitreerobotics/unitree_ros/tree/master/robots/go2_description) 
- [CHAMP Robots (configs)](https://github.com/chvmp/robots)
- [CHAMP Controller](https://github.com/chvmp/champ)
- [Velodyne Simulator](https://github.com/rahgirrafi/velodyne_simulator_ros2_gz.git)

## Tested on:
- Ubuntu 22.04 (ROS 2 Humble)
- Ignition Fortress (Gazebo)

## Features:

- ✅ Go2 robot configured with CHAMP controller
- ✅ Robot description ported to ROS 2
    - ✅ URDF with ros2_control tags
    - ✅ Launch files for ROS 2
    - ✅ Configuration files for ROS 2
- ✅ Ignition Fortress simulation
- ✅ RViz visualization
- ✅ Teleoperation support
- ✅ IMU sensor
- ✅ 2D LiDAR (Hokuyo)
- ✅ 3D LiDAR (Velodyne VLP-16)
- ⬜ SLAM integration
- ⬜ Nav2 integration

## 1. Installation

### 1.0 Clone the repository:
    
```bash
cd <your_ws>/src
git clone https://github.com/rahgirrafi/unitree-go2-ros2.git
cd unitree-go2-ros2

# Initialize and update the velodyne submodule
git submodule update --init --recursive
```

> **Note:** The velodyne lidar package is included as a git submodule. If you've already cloned the repository without the `--recursive` flag, run `git submodule update --init --recursive` to fetch the submodule.

### 1.1 Install dependencies using rosdep:

```bash
# Install rosdep if not already installed
sudo apt install -y python3-rosdep libignition-msgs8-dev

# Initialize rosdep (only needed once)
sudo rosdep init  # Skip if already initialized
rosdep update

# Install all dependencies
cd <your_ws>
rosdep install --from-paths src --ignore-src -r -y
```

### 1.2 Build your workspace:
```bash
cd <your_ws>
colcon build
. <your_ws>/install/setup.bash
```
## 2. Quick Start

You don't need a physical robot to run the following demos. All dependencies will be
installed via rosdep.

> **Every terminal** you use must source the workspace first:
> ```bash
> source /opt/ros/humble/setup.bash
> source <your_ws>/install/setup.bash
> ```

### 2.1 Basic Simulation
Run the Ignition Fortress simulation:
```bash
ros2 launch go2_config gazebo.launch.py
```
This starts Ignition, spawns the Go2, loads the `ros2_control` controllers, and brings up
the CHAMP gait controller and state estimator. The robot stands up after a few seconds
once the controllers are active.

![Go2 Gazebo Launch](.docs/gz.png)

### 2.2 Simulation with RViz
Run the simulation with RViz visualization:
```bash
ros2 launch go2_config gazebo.launch.py rviz:=true
```
![Go2 Gazebo RViz Launch](.docs/gz_rviz.png)

### 2.3 Teleoperation
With the simulation already running, open a **second terminal**:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Keep this terminal focused while pressing keys. It publishes to `/cmd_vel`, which the
gait controller converts into footstep trajectories.

### 2.4 Velodyne 3D LiDAR Simulation
Run the simulation with Velodyne VLP-16 3D LiDAR:
```bash
ros2 launch go2_config gazebo_velodyne.launch.py
```
![Go2 Velodyne Gazebo Launch](.docs/velodyne.png)

### 2.5 Velodyne with RViz Point Cloud
Run the Velodyne simulation with RViz to visualize point cloud data:
```bash
ros2 launch go2_config gazebo_velodyne.launch.py rviz:=true
```

> **Note:** Set point cloud topic to `/velodyne_points` in RViz.

![Go2 Velodyne Gazebo RViz Launch](.docs/velodyne_rviz_pcl.png)

### 2.6 Hokuyo 2D LiDAR Configuration

The 2D laser scanner is enabled with the `laser:=true` launch argument -- no file editing
or rebuild required.

Add the Hokuyo to the standard simulation:
```bash
ros2 launch go2_config gazebo.launch.py laser:=true
```

Or use it *instead of* the Velodyne VLP-16:
```bash
ros2 launch go2_config gazebo_velodyne.launch.py laser:=true rviz:=true
```

The scanner publishes `sensor_msgs/LaserScan` on `/scan` in the `front_laser` frame,
which is the topic the SLAM and Nav2 configs in `go2_config/config/autonomy/` expect.

> **Note:** Set the LaserScan topic to `/scan` in RViz.

Confirm scans are actually flowing before moving on to SLAM:
```bash
ros2 topic hz /scan          # expect ~50 Hz
ros2 topic echo /scan --once # frame_id should be "front_laser"
```

### 2.7 SLAM (Mapping)

SLAM needs the 2D scanner, so launch the simulation with `laser:=true`.

**Terminal 1** -- simulation:
```bash
ros2 launch go2_config gazebo.launch.py laser:=true
```

**Terminal 2** -- slam_toolbox:
```bash
ros2 launch go2_config slam.launch.py sim:=true rviz:=true
```

**Terminal 3** -- drive the robot around to build the map:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Save the map when you are happy with it. `navigate.launch.py` loads
`go2_config/maps/map.yaml` by default, so overwrite that one:
```bash
ros2 run nav2_map_server map_saver_cli \
  -f <your_ws>/src/unitree-go2-ros2/robots/configs/go2_config/maps/map
```

> **Note:** That writes into `src/`, so run `colcon build` again for the new map to reach
> the install space. To skip the rebuild, either save straight into
> `<your_ws>/install/go2_config/share/go2_config/maps/map`, or pass the map explicitly:
> `ros2 launch go2_config navigate.launch.py sim:=true map:=/absolute/path/to/map.yaml`

> **Note:** `sim:=true` sets `use_sim_time` for the SLAM stack. Omitting it against a
> simulated robot makes scan matching fail, because the timestamps come from `/clock`.

### 2.8 Autonomous Navigation

Uses the map saved in the previous step.

**Terminal 1** -- simulation:
```bash
ros2 launch go2_config gazebo.launch.py laser:=true
```

**Terminal 2** -- Nav2:
```bash
ros2 launch go2_config navigate.launch.py sim:=true rviz:=true
```

In RViz, set the robot's starting pose with **2D Pose Estimate**, then send it somewhere
with **2D Goal Pose**.

### 2.9 Launch Argument Reference

| Argument | Default | Applies to | Description |
|----------|---------|------------|-------------|
| `laser` | `false` | `gazebo`, `gazebo_velodyne`, `bringup` | Mount the Hokuyo 2D scanner and publish `/scan`. On `gazebo_velodyne` it *replaces* the VLP-16. |
| `rviz` | `false` | all | Launch RViz alongside the stack |
| `sim` | `false` | `slam`, `navigate`, `bringup` | Use `/clock` simulation time. Set `true` whenever Gazebo is running. |
| `world` | `default.sdf` | `gazebo`, `gazebo_velodyne` | World file to load (see `go2_config/worlds/`) |
| `world_init_x/y/z` | `0.0`/`0.0`/`0.275` | `gazebo`, `gazebo_velodyne` | Robot spawn pose |
| `headless` | `False` | `gazebo`, `gazebo_velodyne` | Run Ignition without the GUI |
| `hardware_connected` | `false` | `bringup` | Set `true` when running against the physical robot |

`slam.launch.py` and `navigate.launch.py` take no `laser` argument -- they do not build a
robot description, they only consume `/scan` from whichever simulation or robot is already
running.

## 3. Tuning Gait Parameters

The gait configuration for your robot can be found in `go2_config/config/gait/gait.yaml`.

![CHAMP Setup Assistant](https://raw.githubusercontent.com/chvmp/champ_setup_assistant/master/docs/images/gait_parameters.png)

| Parameter | Unit | Description |
|-----------|------|-------------|
| **Knee Orientation** | - | How the knees should be bent. Configure as `.>>` `.><` `.<<` `.<>` where dot is the front of the robot. |
| **Max Linear Velocity X** | m/s | Robot's maximum forward/reverse speed. |
| **Max Linear Velocity Y** | m/s | Robot's maximum speed when moving sideways. |
| **Max Angular Velocity Z** | rad/s | Robot's maximum rotational speed. |
| **Stance Duration** | s | How long each leg spends on the ground while walking. Default: 0.25s. |
| **Leg Swing Height** | m | Trajectory height during swing phase. |
| **Leg Stance Height** | m | Trajectory depth during stance phase. |
| **Robot Walking Height** | m | Distance from hip to ground while walking. Setting too high can cause instability. |
| **CoM X Translation** | m | Shift reference point in X axis to compensate for uneven weight distribution. |
| **Odometry Scaler** | - | Multiplier for dead reckoning velocities. Typically 1.0 to 1.20. |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source. See individual package licenses for details.

## Acknowledgements

This project builds upon and incorporates work from the following projects:

* [Unitree Robotics](https://github.com/unitreerobotics/unitree_ros) - Go2 robot description (URDF model)
* [CHAMP](https://github.com/chvmp/champ) - Quadruped controller framework
* [CHAMP Robots](https://github.com/chvmp/robots) - Robot configurations and setup examples
* [Velodyne Simulator](https://github.com/rahgirrafi/velodyne_simulator_ros2_gz.git) - Velodyne LiDAR simulation for Ignition Fortress

We are grateful to the developers and contributors of these projects for their valuable work.
