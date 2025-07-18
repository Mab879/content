---
documentation_complete: true

metadata:
    SMEs:
        - marcusburghardt
        - vojtapolasek

title: 'ANSSI-BP-028 (high)'

description: |-
    This is a draft profile for experimental purposes.
    This draft profile contains configurations that align to ANSSI-BP-028 v2.0 at the high hardening level.

    ANSSI is the French National Information Security Agency, and stands for Agence nationale de la sécurité des systèmes d'information.
    ANSSI-BP-028 is a configuration recommendation for GNU/Linux systems.

    A copy of the ANSSI-BP-028 can be found at the ANSSI website:
    https://www.ssi.gouv.fr/administration/guide/recommandations-de-securite-relatives-a-un-systeme-gnulinux/

    An English version of the ANSSI-BP-028 can also be found at the ANSSI website:
    https://cyber.gouv.fr/publications/configuration-recommendations-gnulinux-system

selections:
    - anssi:all:high
    - var_password_hashing_algorithm_pam=yescrypt
    - var_authselect_profile=local
    # the following rule renders UEFI systems unbootable
    - '!sebool_secure_mode_insmod'
    # Following rules are incompatible with rhel10 product
    - '!enable_authselect'
    # tally2 is deprecated, replaced by faillock
    - '!accounts_passwords_pam_tally2_deny_root'
    - '!accounts_passwords_pam_tally2'
    - '!accounts_passwords_pam_tally2_unlock_time'
    # RHEL 10 does not support 32 bit architecture
    - '!install_PAE_kernel_on_x86-32'
    # this timer does not exist in RHEL 10
    - '!aide_periodic_checking_systemd_timer'
    # the package does not exist in RHEL 10
    - '!package_dracut-fips-aesni_installed'
    # pam_cracklib is not used in RHEL 10
    - '!cracklib_accounts_password_pam_lcredit'
    - '!cracklib_accounts_password_pam_ocredit'
    - '!cracklib_accounts_password_pam_ucredit'
    - '!cracklib_accounts_password_pam_minlen'
    - '!cracklib_accounts_password_pam_dcredit'
    # umask is configured at a different place in RHEL 10
    - '!sudo_add_umask'
    # Non-Red Hat keys are irrelevant on RHEL 10
    - '!ensure_oracle_gpgkey_installed'
    - '!ensure_almalinux_gpgkey_installed'
    # this rule is not automated anymore
    - '!security_patches_up_to_date'
    # There is only chrony package on RHEL 10, no ntpd
    - '!service_chronyd_or_ntpd_enabled'
    - 'service_chronyd_enabled'
    # RHEL 10 unified the paths for grub2 files. These rules are selected in control file by R29.
    - '!file_groupowner_efi_grub2_cfg'
    - '!file_owner_efi_grub2_cfg'
    - '!file_permissions_efi_grub2_cfg'
    - '!file_groupowner_efi_user_cfg'
    - '!file_owner_efi_user_cfg'
    - '!file_permissions_efi_user_cfg'
    # RHEL 10 unified the paths for grub2 files. This rule is selected in control file by R5.
    - '!grub2_uefi_password'
    # disable R45: Enable AppArmor security profiles
    - '!apparmor_configured'
    - '!all_apparmor_profiles_enforced'
    - '!grub2_enable_apparmor'
    - '!package_apparmor_installed'
    - '!package_pam_apparmor_installed'
    # these packages do not exist in rhel10 (R62)
    - '!package_dhcp_removed'
    - '!package_rsh_removed'
    - '!package_rsh-server_removed'
    - '!package_sendmail_removed'
    - '!package_talk_removed'
    - '!package_talk-server_removed'
    - '!package_xinetd_removed'
    - '!package_ypbind_removed'
    - '!package_ypserv_removed'
    # RHEL 10 uses a different rule for auditing changes to selinux configuration (R73)
    - '!audit_rules_mac_modification'
    - audit_rules_mac_modification_etc_selinux
    # these rules are failing when they are remediated with Ansible, removing them temporarily until they are fixed
    - '!accounts_password_pam_retry'
    # These rules are being modified and they are causing trouble in their current state (R67)
    - '!sssd_enable_pam_services'
    - '!sssd_ldap_configure_tls_reqcert'
    - '!sssd_ldap_start_tls'
    # These rules are no longer relevant
    - '!prefer_64bit_os'
    - '!kernel_config_devkmem'
    - '!kernel_config_hardened_usercopy_fallback'
    - '!kernel_config_page_poisoning_no_sanity'
    - '!kernel_config_page_poisoning_zero'
    - '!kernel_config_page_table_isolation'
    - '!kernel_config_refcount_full'
    - '!kernel_config_retpoline'
    - '!kernel_config_security_writable_hooks'
