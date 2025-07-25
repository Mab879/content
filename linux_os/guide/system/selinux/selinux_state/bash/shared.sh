# platform = multi_platform_rhel,multi_platform_fedora,multi_platform_ol,multi_platform_rhv,multi_platform_sle,multi_platform_slmicro,multi_platform_almalinux
# reboot = true
# strategy = restrict
# complexity = low
# disruption = low

{{{ bash_instantiate_variables("var_selinux_state") }}}

{{{ bash_selinux_config_set(parameter="SELINUX", value="$var_selinux_state", rule_id=rule_id) }}}

fixfiles onboot
