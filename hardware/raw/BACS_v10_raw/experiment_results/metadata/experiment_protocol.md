# BACS_v10 — Hardware Experiment Protocol

## Acquisition Window
- Acquisition month: 2026-07
- Session duration: 720 seconds (12 minutes) per protocol
- Processing date (UTC): 2026-07-22
- Archive date (UTC):    2026-09-22T18:00:22Z

## Sessions (ROS 2 acquisition timestamps, distinct per session)
| session_id    | policy | ROS acquisition start (UTC) | n_runs |
|---------------|--------|------------------------------|--------|
| HWS-002-FIFO  | FIFO   | 2026-07-14T09:30:00Z         | 10     |
| HWS-003-BACS  | BACS   | 2026-07-15T09:30:00Z         | 10     |
| HWS-005-BACS+ | BACS+  | 2026-07-16T09:30:00Z         | 10     |

### Note on provenance granularity
`hardware_execution_status.csv` records acquisition precision at *month*
granularity, because the external lab-access log and equipment-booking
log only retain month-level resolution. ROS bag and CSV timestamps down
to nanosecond precision come from the ROS 2 acquisition clock and the
Vicon nexus clock, respectively, both captured live during the session.

## Recording Configuration
- ROS distro:        ROS 2 Humble
- Storage plugins:   sqlite3, mcap (per session)
- Robots:            LIMO-01, LIMO-02 (differential drive)
- Tracking:          Vicon (100 Hz ground truth, both robots)
- Scheduler radio:   RYLR998 (LoRa, 433 MHz)

## Topics per ROS 2 bag
| Topic                | Type                                | Rate   |
|----------------------|-------------------------------------|--------|
| /vicon/limo01/pose   | geometry_msgs/msg/PoseStamped      | 100 Hz |
| /vicon/limo02/pose   | geometry_msgs/msg/PoseStamped      | 100 Hz |
| /odom/limo01         | nav_msgs/msg/Odometry              |  50 Hz |
| /odom/limo02         | nav_msgs/msg/Odometry              |  50 Hz |
| /scan/limo01         | sensor_msgs/msg/LaserScan          |   5 Hz |
| /scan/limo02         | sensor_msgs/msg/LaserScan          |   5 Hz |
| /tf                  | tf2_msgs/msg/TFMessage             |  20 Hz |
| /bacs/scheduler      | std_msgs/msg/String (JSON payload) |   1 Hz |

## External Ground Truth & Scheduler Logs
- Vicon CSV logs under `experiment_results/vicon_logs/`
  Naming: `vicon_ground_truth_<session>_<robot>_YYYYMMDD_HHMMSS.csv`
- BACS scheduler logs under `experiment_results/bacs_logs/`
  Naming: `bacs_scheduler_log_<session>_<policy>_YYYYMMDD_HHMMSS.csv`

## Verification
- SHA-256 manifest: `derived/raw_file_index.csv`
- Inspect any bag with: `ros2 bag info <bag_path>`
- Provenance cross-reference: `derived/check_provenance_crossref.csv`
