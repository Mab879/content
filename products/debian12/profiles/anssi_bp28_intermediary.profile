documentation_complete: true

title: 'ANSSI-BP-028 (intermediary)'

description: |-
    This profile contains configurations that align to ANSSI-BP-028 v2.0 at the intermediary hardening level.

    ANSSI is the French National Information Security Agency, and stands for Agence nationale de la sécurité des systèmes d'information.
    ANSSI-BP-028 is a configuration recommendation for GNU/Linux systems.

    A copy of the ANSSI-BP-028 can be found at the ANSSI website:
    https://www.ssi.gouv.fr/administration/guide/recommandations-de-securite-relatives-a-un-systeme-gnulinux/

# selinux_state: not applicable
# postfix_client_configure_mail_alias: not applicable. should be exim
# grub2_l1tf_argument debian kernels are not vulnerable, but switching from
# conditional cache flush to force mode prevent protection disabling.

selections:
  - anssi:all:intermediary
  # PASS_MIN_LEN is handled by PAM on debian systems.
  - '!accounts_password_minlen_login_defs'
  # ANSSI BP 28 suggest using libpam_pwquality, which isn't deployed by default
  - 'package_pam_pwquality_installed'
  # PAM honour login.defs file for algorithm
  - 'set_password_hashing_algorithm_logindefs'
  # Debian uses apparmor
  - '!selinux_state'
  # The following are MLS related rules (not part of ANSSI-BP-028)
  - '!accounts_polyinstantiated_tmp'
  - '!accounts_polyinstantiated_var_tmp'
  - '!enable_pam_namespace'
  # there is no tmp.mount unit on Debian 12.
  - '!systemd_tmp_mount_enabled'

  # Following rules once had a prodtype incompatible with the debian12 product
  - '!accounts_passwords_pam_tally2_deny_root'
  - '!ensure_redhat_gpgkey_installed'
  - '!set_password_hashing_algorithm_systemauth'
  - '!package_dnf-automatic_installed'
  - '!dnf-automatic_security_updates_only'
  - '!cracklib_accounts_password_pam_lcredit'
  - '!dnf-automatic_apply_updates'
  - '!cracklib_accounts_password_pam_ocredit'
  - '!accounts_password_pam_unix_rounds_system_auth'
  - '!timer_dnf-automatic_enabled'
  - '!accounts_passwords_pam_tally2'
  - '!cracklib_accounts_password_pam_ucredit'
  - '!file_permissions_unauthorized_sgid'
  - '!ensure_gpgcheck_local_packages'
  - '!accounts_passwords_pam_tally2_unlock_time'
  - '!enable_authselect'
  - '!cracklib_accounts_password_pam_minlen'
  - '!cracklib_accounts_password_pam_dcredit'
  - '!ensure_gpgcheck_globally_activated'
  - '!file_permissions_unauthorized_suid'
  - '!ensure_gpgcheck_never_disabled'
  - '!ensure_oracle_gpgkey_installed'
  - '!ensure_almalinux_gpgkey_installed'

  # The following rule is not applicable to Debian 12
  - '!logind_session_timeout'
