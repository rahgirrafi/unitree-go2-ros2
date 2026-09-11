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
- ✅ Selectable locomotion controller (CHAMP gait controller or an RL policy)

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

### 2.9 Choosing the Locomotion Controller

Both simulation launch files take a `controller` argument that selects what generates
joint commands:

```bash
# CHAMP gait controller (default, unchanged behaviour)
ros2 launch go2_config gazebo.launch.py controller:=champ

# RL policy trained in IsaacLab
ros2 launch go2_config gazebo.launch.py controller:=model
```

Everything else is identical between the two. The CHAMP state estimator and both EKFs
run in either mode, so `/odom`, TF, SLAM and Nav2 work the same way regardless — the
teleop and navigation sections above apply unchanged:

```bash
ros2 launch go2_config gazebo.launch.py laser:=true controller:=model
ros2 launch go2_config navigate.launch.py sim:=true rviz:=true
```

| | `controller:=champ` | `controller:=model` |
|---|---|---|
| Joint commands from | `quadruped_controller_node` | `rl_policy_node.py` |
| ros2_control controller | `joint_group_effort_controller` (trajectory + PID) | `rl_joint_effort_controller` (group effort) |
| `/cmd_vel` consumer | gait controller | policy, clipped to its trained command range |
| State estimation, EKFs, `/odom`, TF | running | running |

Only one ros2_control controller is loaded, since both claim the same effort command
interfaces — that is what makes the switch exclusive.

---

### 2.10 Launch Argument Reference

| Argument | Default | Applies to | Description |
|----------|---------|------------|-------------|
| `laser` | `false` | `gazebo`, `gazebo_velodyne`, `bringup` | Mount the Hokuyo 2D scanner and publish `/scan`. On `gazebo_velodyne` it *replaces* the VLP-16. |
| `controller` | `champ` | `gazebo`, `gazebo_velodyne`, `bringup` | `champ` for the CHAMP gait controller, `model` for the IsaacLab-trained RL policy |
| `checkpoint` | from `config/rl/policy.yaml` | `gazebo`, `gazebo_velodyne` | rsl_rl checkpoint to run when `controller:=model` |
| `rviz` | `false` | all | Launch RViz alongside the stack |
| `sim` | `false` | `slam`, `navigate`, `bringup` | Use `/clock` simulation time. Set `true` whenever Gazebo is running. |
| `world` | `default.sdf` | `gazebo`, `gazebo_velodyne` | World file to load (see `go2_config/worlds/`) |
| `world_init_x/y/z` | `0.0`/`0.0`/`0.275` | `gazebo`, `gazebo_velodyne` | Robot spawn pose |
| `headless` | `False` | `gazebo`, `gazebo_velodyne` | Run Ignition without the GUI |
| `hardware_connected` | `false` | `bringup` | Set `true` when running against the physical robot |

`slam.launch.py` and `navigate.launch.py` take no `laser` argument -- they do not build a
robot description, they only consume `/scan` from whichever simulation or robot is already
running.

## 3. Using Your Own RL Policy

This section is the full recipe for taking a policy you trained in IsaacLab and driving
the robot with it.

### 3.1 What is supported

`rl_policy_node.py` rebuilds the actor network **directly from an rsl_rl checkpoint's
`model_state_dict`**, so neither rsl_rl nor IsaacLab has to be importable at runtime.
Out of the box it supports:

* rsl_rl `OnPolicyRunner` checkpoints — the `model_*.pt` files written into
  `logs/rsl_rl/<experiment>/<run>/`, which contain `actor.*` weights. (A TorchScript
  file exported by `export_policy_as_jit` is *not* what this loads.)
* A plain MLP `ActorCritic` of any layer sizes, with `elu`, `relu` or `tanh`.
* The standard IsaacLab velocity-tracking observation, in this exact order:
  `base_lin_vel(3)`, `base_ang_vel(3)`, `projected_gravity(3)`, `velocity_commands(3)`,
  `joint_pos_rel(12)`, `joint_vel_rel(12)`, `last_action(12)`, `height_scan(N)`.
* A `JointPositionAction` with a scale and `use_default_offset: true`.

Anything outside that — an RNN policy, observation history, a different term order,
`empirical_normalization` — needs a code change, described in [3.5](#35-when-you-need-to-touch-the-code).

The only runtime dependency is PyTorch (`pip install torch`). CPU is plenty enough for inference.
Core i5 10th gen CPU measures ~0.1 ms against a 20 ms budget.

### 3.2 Point it at your checkpoint

The quickest path, with no file editing at all:

```bash
ros2 launch go2_config gazebo.launch.py controller:=model \
  checkpoint:=/path/to/logs/rsl_rl/<experiment>/<run>/model_999.pt
```

To make it the default, edit `checkpoint:` in
`robots/configs/go2_config/config/rl/policy.yaml` — the launch file reads its default
from that file, so there is only one place to change.

If your policy is a drop-in retrain of the same task, this is all you need. If you
changed the environment at all, work through 3.3 before trusting it.

### 3.3 Transfer your training config

Every value the policy depends on lives in `go2_config/config/rl/policy.yaml`. Each one
has a counterpart in the `params/env.yaml` and `params/agent.yaml` that IsaacLab wrote
next to your checkpoint. **Go through this table whenever you retrain** — a mismatch here
does not throw an error, it just produces a robot that walks badly or falls over.

| `policy.yaml` key | Comes from | Notes |
|---|---|---|
| `hidden_dims` | `agent.yaml` → `policy.actor_hidden_dims` | Checked against the checkpoint at startup; a mismatch is a hard error |
| `activation` | `agent.yaml` → `policy.activation` | |
| `policy_rate` | `env.yaml` → `1 / (sim.dt × decimation)` | e.g. `1/(0.005 × 4)` = 50 Hz |
| `action_scale` | `env.yaml` → `actions.joint_pos.scale` | Target is `q_default + scale × action` |
| `default_joint_pos` | `env.yaml` → `scene.robot.init_state.joint_pos` | Regex patterns there; expand them **in policy joint order** (see 3.4) |
| `kp`, `kd`, `torque_limit` | `env.yaml` → `scene.robot.actuators.<group>` | `stiffness`, `damping`, `effort_limit` |
| `max_lin_vel_x/y`, `max_ang_vel_z` | `env.yaml` → `commands.base_velocity.ranges` | `/cmd_vel` is clipped to these; the policy never saw anything outside them |
| `height_scan_dim` | `env.yaml` → `scene.height_scanner.pattern_cfg` | `(size_x/res + 1) × (size_y/res + 1)`; e.g. 1.6×1.0 at 0.1 → 17 × 11 = **187** |
| `height_scan_constant` | measured, see 3.4 | |

Check `agent.yaml` says `empirical_normalization: null` and
`policy.actor_obs_normalization: false`. If either is on, the checkpoint carries a
running mean/std that must be applied to the observation before inference, and the node
does not do that yet.

### 3.4 The two settings that are easy to get wrong

**Joint order.** IsaacLab orders an articulation's joints breadth-first — all four hips,
then all four thighs, then all four calves — and names them `FL/FR/RL/RR`. This repo uses
CHAMP names. `ros_joint_names` in `policy.yaml` holds the mapping, index by index:

| Policy index | IsaacLab | This repo |
|---|---|---|
| 0–3 | `FL_hip`, `FR_hip`, `RL_hip`, `RR_hip` | `lf_hip_joint`, `rf_hip_joint`, `lh_hip_joint`, `rh_hip_joint` |
| 4–7 | `FL_thigh`, `FR_thigh`, `RL_thigh`, `RR_thigh` | `lf_upper_leg_joint`, `rf_upper_leg_joint`, `lh_upper_leg_joint`, `rh_upper_leg_joint` |
| 8–11 | `FL_calf`, `FR_calf`, `RL_calf`, `RR_calf` | `lf_lower_leg_joint`, `rf_lower_leg_joint`, `lh_lower_leg_joint`, `rh_lower_leg_joint` |

`default_joint_pos` must be expanded in this same order, and the `joints:` list of
`rl_joint_effort_controller` in
`go2_description/config/ros_control/ros_control.yaml` must match it too — that list
defines which effort in the published array goes to which joint.

If you are unsure of your own asset's ordering, print it once in IsaacLab with
`env.scene["robot"].data.joint_names` and copy it. Getting this wrong gives you a robot
that thrashes, not one that limps.

**Height scan.** If your environment has a height scanner, those rays are usually most of
the observation (187 of 235 in the rough task) and Gazebo has no equivalent sensor. Every
world shipped here is a flat ground plane, where the entire grid collapses to one
constant:

```
height_scan_constant = walking_base_height − 0.5
```

The 0.5 is the `offset` argument of `mdp.height_scan`. Measure the first term by standing
the robot up and reading `ros2 topic echo /odom_ground_truth` — this policy walks at
0.40 m, hence `−0.10`. It is worth doing: going from `−0.15` to `−0.10` took forward
tracking from 0.15 m/s to 0.44 m/s against a 0.5 m/s command and cut lateral drift over
12 s from 2.3 m to 0.5 m.

If your policy has **no** height scanner (the flat task, for example), set
`height_scan_dim: 0` and the term disappears from the observation.

> **On a world with real uneven terrain the constant is wrong** and the policy is
> effectively blind, since it reports flat ground everywhere. That case needs a real
> ray-cast sensor bridged into the node — replace `self.height_scan` in
> `rl_policy_node.py` with live sensor data.

### 3.5 When you need to touch the code

The node builds its observation in one place — `policy_step()` in
`go2_config/scripts/rl_policy_node.py`. Edit that function if your `env.yaml`'s
`observations.policy` block lists different terms, or the same terms in a different
order.

The startup check catches a *size* mismatch and refuses to run:

```
policy expects a 235-dim observation but the configured terms build 48
```

It cannot catch a *reordering* — same width, wrong meaning — so compare your
`observations.policy` block against the order listed in 3.1 by eye.

### 3.6 Run it and check it worked

```bash
ros2 launch go2_config gazebo.launch.py controller:=model
```

Then, in a second terminal, walk down this list:

```bash
# 1. Both controllers active? (not "unconfigured")
ros2 control list_controllers

# 2. IMU alive? Must be ~100 Hz. Silence here makes the policy think it is
#    always perfectly level, and it will flip over as soon as it tilts.
ros2 topic hz /imu/data

# 3. Policy loaded and commanding? Look for "loaded policy from ..." then
#    "stand-up complete, policy taking over"
ros2 topic hz /rl_joint_effort_controller/commands

# 4. Standing? z should settle around 0.3-0.4 m with small roll/pitch
ros2 topic echo /odom_ground_truth --once

# 5. Drive it
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### 3.7 Troubleshooting

| Symptom | Cause |
|---|---|
| Node exits: `policy expects a N-dim observation but the configured terms build M` | `height_scan_dim` wrong, or your observation has different terms — see 3.3 and 3.5 |
| Node exits: `checkpoint hidden dims [...] do not match configured [...]` | `hidden_dims` does not match `agent.yaml` |
| Node exits: `joint missing from /joint_states` | A name in `ros_joint_names` is not in the URDF |
| Robot lies there inert, no torques | Controllers stuck `unconfigured` — see the note below |
| Robot thrashes violently | Joint order wrong (3.4) |
| Robot walks, then flips onto its back | `/imu/data` not publishing — check with `ros2 topic hz /imu/data` |
| Robot belly-flops and never gets up | `stand_kp`/`stand_kd` too soft for the spawn pose |
| Walks, but weakly or drifting sideways | `height_scan_constant` off (3.4), or the policy is simply undertrained |

> **Controller startup race.** `champ_gazebo` waits a fixed 5–6 s for
> `controller_manager` before loading controllers. On a slow start that race is lost and
> they stay `unconfigured`, leaving the robot inert. Recover without relaunching:
> ```bash
> for c in joint_states_controller rl_joint_effort_controller; do
>   ros2 control set_controller_state $c inactive
>   ros2 control set_controller_state $c active
> done
> ```

### 3.8 How the node works

Two loops run at different rates, mirroring how the policy was trained:

| Loop | Rate | Does |
|------|------|------|
| Policy | 50 Hz (`sim.dt` × `decimation`) | Builds the observation, runs the actor, turns actions into joint position targets (`q_default + scale × a`) |
| PD | 200 Hz | `τ = kp·(q* − q) − kd·q̇`, clipped to `±torque_limit`, published to `rl_joint_effort_controller` |

The PD loop runs faster than the policy because IsaacLab drove the joints with an
implicit PD actuator at the physics rate; holding one torque for a whole 20 ms policy
step visibly under-damps the legs.

On startup the robot eases into the trained default stance over 2 s before the policy
takes over, so its first observation is one it has actually seen. That stand-up phase
uses its own stiffer gains (`stand_kp`/`stand_kd`, default 100/2): Gazebo spawns the
robot with every joint at its URDF zero, which is a sprawl, and it lands on its belly —
the trained gains are far too soft to push it back up, because IsaacLab never had to,
having initialised the robot already standing.

Two supporting sensor fixes came out of building this, and both benefit the CHAMP path:

* **`/imu/data` never published anything.** Ignition scopes sensor topics by world, model
  and link and ignores the `<topic>` on the sensor, so the bridge has to ask for
  `/world/<world>/model/<robot>/link/base_link/sensor/imu_sensor/imu` — bridging a bare
  `/imu/data` silently yields no messages at all. The policy needs it for
  `projected_gravity`. CHAMP defaults to `orientation_from_imu:=false`, which is why this
  went unnoticed.
* **Ground-truth base velocity** comes from an Ignition `OdometryPublisher` added to the
  description and bridged to `/odom_ground_truth`, since the IMU gives only orientation
  and angular velocity. Its twist is reported in the body frame, which is what the policy
  was trained on (verified against numerically differentiated world-frame motion).

### 3.9 Verified behaviour

Measured in the default world with `model_999.pt`, commanding 0.5 m/s forward for 12 s:
the robot stands up, walks 4.58 m (vx steady 0.41–0.45 m/s), drifts 0.54 m laterally and
stays upright throughout (roll ≈ 3°, pitch ≈ 3°, base height ≈ 0.40 m). It also walks
backwards, strafes and turns.

Velocity tracking is loose, and that is the policy rather than the bridge — this training
run finishes at `Metrics/base_velocity/error_vel_xy` ≈ 0.42 m/s and `error_vel_yaw` ≈
0.47 rad/s, with 9% of episodes still ending in a base-ground contact. Train longer if
you want tighter tracking.

Only the simulation paths are wired for `controller:=model`; the policy has not been run
against physical hardware.

## 4. Tuning Gait Parameters

This applies to `controller:=champ`. The gait configuration for your robot can be found in `go2_config/config/gait/gait.yaml`.

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
