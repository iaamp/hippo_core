#pragma once

#include <array>
#include <eigen3/Eigen/Dense>

namespace hippo_control {
namespace motor_failure {
namespace failure_config {
namespace one {
static constexpr int kTopLeft = 0;
static constexpr int kTopRight = 1;
static constexpr int kBottomRight = 2;
static constexpr int kBottomLeft = 3;
}  // namespace one
namespace two {
static constexpr int kTopLeftToBottomRight = 0;
static constexpr int kTopRightToBottomLeft = 1;
}  // namespace two
}  // namespace failure_config

namespace mode {
enum Mode {
  kUnset = -1,
  kIdle = 0,
  kUntangling = 1,
  kNormal = 2,
  kSingleFailureUndetected = 3,
  kDoubleFailureUndetected = 4,
  kSingleFailureDetected = 5,
  kDoubleFailureDetected = 6,
};
}

class MotorFailure {
 public:
  static constexpr double kMotorOffset = 0.069;
  /// factor between force and motor induced torque caused by rotation
  static constexpr double kTorqueFactor = 1.0;
  Eigen::Vector<double, 4> Update(double pitch_rate, double yaw_rate,
                                  double surge_velocity,
                                  const Eigen::Quaterniond &_orientation);
  void SetTarget(double pitch_rate, double yaw_rate, double surge_velocity);

  void SetPGains(double surge, double pitch, double yaw) {
    surge_p_gain_ = surge;
    pitch_p_gain_ = pitch;
    yaw_p_gain_ = yaw;
  }
  void SetLinearDamping(double surge, double pitch, double yaw) {
    surge_damping_linear_ = surge;
    pitch_damping_linear_ = pitch;
    yaw_damping_linear_ = yaw;
  }
  void SetInertia(double surge, double pitch, double yaw) {
    surge_inertia_ = surge;
    pitch_inertia_ = pitch;
    yaw_inertia_ = yaw;
  }
  void SetMode(mode::Mode _mode) {
    mode_ = _mode;
    UpdateMixerMatrix();
  }
  mode::Mode Mode() const { return mode_; };

 private:
  Eigen::Vector<double, 6> ComputeThrusts(
      double surge_velocity, double surge_accel, double pitch_velocity,
      double pitch_accel, double yaw_velocity, double yaw_accel);
  Eigen::Vector<double, 4> AllocateThrust(
      const Eigen::Vector<double, 6> &thrust);
  Eigen::Matrix<double, 6, 4> FullMixerMatrix() const;
  void UpdateMixerMatrix();

  mode::Mode mode_{mode::Mode::kUnset};
  double pitch_rate_target_{0.0};
  double yaw_rate_target_{0.0};
  double surge_velocity_target_{0.0};

  double surge_p_gain_{1.0};
  double pitch_p_gain_{2.0};
  double yaw_p_gain_{2.0};

  double surge_inertia_{3.42};
  double surge_damping_linear_{5.39};
  double pitch_damping_linear_{0.007};
  double yaw_damping_linear_{0.007};
  double pitch_inertia_{0.027};
  double yaw_inertia_{0.027};
  Eigen::Matrix<double, 6, 4> mixer_matrix_;

  double controllability_{0.0};
  Eigen::Vector<double, 6> torque_force_vec_;
};
// TODO
}  // namespace motor_failure
}  // namespace hippo_control
