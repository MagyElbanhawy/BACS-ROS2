# Third-party references

This directory contains external reference implementations and utility repositories that are relevant to the BACS physical-validation stack. These are reference artifacts, not vendored source for the primary project implementation.

## Included references

### Vicon / motion-capture references
- `OPT4SMART/ros2-vicon-receiver`
  - URL: https://github.com/OPT4SMART/ros2-vicon-receiver
  - Relevance: direct ROS 2 driver reference for Vicon ground-truth streams used in the physical experiments.
- `KumarRobotics/motion_capture_system`
  - URL: https://github.com/KumarRobotics/motion_capture_system
  - Relevance: alternative Vicon / motion-capture ROS driver and cross-check for hardware integration.
- `KumarRobotics/vicon2gt`
  - URL: https://github.com/KumarRobotics/vicon2gt
  - Relevance: ground-truth trajectory generation for evaluation pipelines and RMSE analysis.

### RYLR998 LoRa references
- `jmwanderer/RYLR_LoRaAT`
  - URL: https://github.com/jmwanderer/RYLR_LoRaAT
  - Relevance: UART AT-command reference for Reyax RYLR devices.
- `terakilobyte/rylr998-rs`
  - URL: https://github.com/terakilobyte/rylr998-rs
  - Relevance: Rust protocol / host-driver reference for the RYLR998 stack.

## Excluded references
The following were intentionally not added because they are not directly tied to the LIMO + Vicon + RYLR998 stack:
- TIERS UWB drone dataset
- LIAS-CUHKSZ DataProcessTools4SLAM conversion scripts
- Heltec sample LoRa log files

These are useful general references, but they are not directly required for the evidence-backed BACS reproducibility package.
