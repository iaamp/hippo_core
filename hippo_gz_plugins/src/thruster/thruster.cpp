#include "thruster.hpp"

#include <ignition/gazebo/Conversions.hh>
#include <ignition/plugin/Register.hh>

IGNITION_ADD_PLUGIN(thruster::Plugin, ignition::gazebo::System,
                    thruster::Plugin::ISystemConfigure,
                    thruster::Plugin::ISystemPreUpdate)
IGNITION_ADD_PLUGIN_ALIAS(thruster::Plugin, "hippo_gz_plugins::thruster")

namespace thruster {
Plugin::Plugin() : System(), private_(std::make_unique<PluginPrivate>()) {}

void Plugin::Configure(const ignition::gazebo::Entity &_entity,
                       const std::shared_ptr<const sdf::Element> &_sdf,
                       ignition::gazebo::EntityComponentManager &_ecm,
                       ignition::gazebo::EventManager &_eventMgr) {
  private_->ParseSdf(_sdf, _ecm);
  if (!private_->InitModel(_ecm, _entity)) {
    ignerr << "Plugin needs to be attached to model entity." << std::endl;
    return;
  }
  private_->AdvertiseRpm();
  private_->SubscribeThrust();
}
void Plugin::PreUpdate(const ignition::gazebo::UpdateInfo &_info,
                        ignition::gazebo::EntityComponentManager &_ecm) {
  if (_info.paused) {
    return;
  }
   // Apply forces/moments in each step
  private_->UpdateRotorVelocity(_ecm, std::chrono::duration<double>(_info.dt).count());
  private_->ApplyWrench(_ecm);

  // publish messages with specified update rate
  auto dt = _info.simTime - private_->last_pub_time_;
  if ((dt > std::chrono::steady_clock::duration::zero()) &&
      (dt < private_->update_period_)) {
    return;
  }

  private_->last_pub_time_ = _info.simTime;
  private_->PublishRpm(_ecm);
}
}  // namespace thruster
